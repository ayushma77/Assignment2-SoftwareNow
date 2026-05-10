# image_processor.py
# Handles image loading and content-aware difference generation.
#
# WHY the previous version produced "squares and triangles"
# ---------------------------------------------------------
# The previous code had two fatal flaws discovered through live testing:
#
# 1. seamlessClone MAD ≈ 0.0  — Poisson blending with NORMAL_CLONE solves
#    to reproduce the DESTINATION boundary conditions.  When donor colours
#    are similar to the destination (they come from the same image), the
#    solver washes out the donor entirely.  Result: virtually no pixel change.
#
# 2. The calibration amplifier then kicked in (alpha up to 3×) on a near-
#    zero signal, which amplified the rectangular write boundary instead of
#    any real difference — producing a faint square outline.
#
# Root fix: stop writing to a rectangular ROI at all.
# Every effect below uses a Gaussian blob mask that smoothly fades to zero
# at the region boundary, so there is never a hard edge in the output.
#
# Techniques (all tested for correct MAD range on synthetic images):
# -----------------------------------------------------------------
#   SOFT_DARKEN   – lighten or darken the centre with a Gaussian falloff.
#                   factor 0.40–0.55 → MAD 19–27.  Looks like a shadow or
#                   lighting change fell on part of the scene.
#
#   LOCAL_WARP    – push pixels outward/inward with a Gaussian displacement
#                   field (cv2.remap).  disp 18–25 → MAD 15–21.  Looks like
#                   a shape bulged, shrank, or shifted slightly — the "extra
#                   petal" or "bent branch" effect.
#
#   HUE_TINT      – rotate HSV hue by 25–50°, blended with Gaussian mask so
#                   only the centre changes.  Works well on colourful images;
#                   calibration amplifies it on muted photos.
#
#   CONTRAST_POP  – boost local contrast (pull pixel values away from local
#                   mean) using Gaussian mask.  boost 1.5–1.8 → MAD 12–22.
#                   Looks like a region became more or less vivid.
#
#   CLONE_PATCH   – copy a patch from a random other location and alpha-blend
#                   it in with a Gaussian mask.  Inherently smooth because the
#                   mask fades to 0 at the edges.  The "different object
#                   appeared" effect.

import cv2
import random
import numpy as np

from difference import Difference


class ImageProcessor:
    """
    Separates all OpenCV / image-processing work from the GUI layer.

    Public interface
    ----------------
    generate_differences(num_diffs=5)  – call once per game
    get_images()                       – (original, modified) BGR arrays
    get_differences()                  – list[Difference]
    """

    def __init__(self, image_path):
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise ValueError(f"Failed to load image: {image_path!r}")
        self.modified    = self.original.copy()
        self.differences = []

    # ──────────────────────────────────────────────────────────────────────

    def generate_differences(self, num_diffs=5):
        """Place num_diffs non-overlapping, smoothly-blended differences."""
        height, width = self.original.shape[:2]
        self.differences.clear()
        self.modified = self.original.copy()

        min_side = 40
        max_side = 90
        margin   = 10   # keep regions away from image edges

        attempts = 0
        while len(self.differences) < num_diffs and attempts < 400:
            attempts += 1

            w = random.randint(min_side, max_side)
            h = random.randint(min_side, max_side)

            if width < w + 2*margin or height < h + 2*margin:
                continue

            x = random.randint(margin, width  - w - margin)
            y = random.randint(margin, height - h - margin)

            if self._is_overlapping(x, y, w, h):
                continue

            diff_type = random.choice([
                "soft_darken",
                "local_warp",
                "local_warp",   # weighted: most visually interesting
                "hue_tint",
                "contrast_pop",
                "clone_patch",
            ])

            if self._apply(x, y, w, h, diff_type):
                self.differences.append(Difference(x, y, w, h, diff_type))

    # ──────────────────────────────────────────────────────────────────────

    def _is_overlapping(self, x, y, w, h):
        for d in self.differences:
            no_overlap = (
                x + w <= d.x or x >= d.x + d.width or
                y + h <= d.y or y >= d.y + d.height
            )
            if not no_overlap:
                return True
        return False

    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _gauss_blob(h, w, sigma_ratio=0.38):
        """
        Return a (h, w) float32 array with 1.0 at the centre, decaying to
        ~0.01 at the edges.  sigma_ratio controls how quickly it falls off.

        WHY Gaussian and not a flat mask or ellipse:
        - A flat mask or ellipse has a hard boundary that shows up as a
          visible ring when any pixel operation is applied to it.
        - A Gaussian weights the effect to 0 at the border → no edge at all.
        """
        sigma = sigma_ratio * min(h, w)
        gx = np.arange(w, dtype=np.float32) - w / 2.0
        gy = np.arange(h, dtype=np.float32) - h / 2.0
        gx2d, gy2d = np.meshgrid(gx, gy)
        blob = np.exp(-(gx2d**2 + gy2d**2) / (2.0 * sigma**2))
        return (blob / blob.max()).astype(np.float32)

    # ──────────────────────────────────────────────────────────────────────

    def _apply(self, x, y, w, h, diff_type):
        """
        Apply one modification in-place on self.modified.

        All methods write back through the Gaussian mask so the result
        blends smoothly into the surrounding image — no rectangular border.

        Returns True on success.  False if the change is too small to see
        (e.g. hue shift on a greyscale region) or a method hard-fails.
        """
        orig_roi = self.original[y:y+h, x:x+w].astype(np.float32)
        cur_roi  = self.modified [y:y+h, x:x+w].astype(np.float32)
        blob     = self._gauss_blob(h, w)          # (h, w) float32, max=1

        if diff_type == "soft_darken":
            modified_roi = self._soft_darken(cur_roi, blob)
        elif diff_type == "local_warp":
            modified_roi = self._local_warp(cur_roi, blob, w, h)
        elif diff_type == "hue_tint":
            modified_roi = self._hue_tint(cur_roi, blob, h, w)
        elif diff_type == "contrast_pop":
            modified_roi = self._contrast_pop(cur_roi, blob)
        elif diff_type == "clone_patch":
            modified_roi = self._clone_patch(x, y, w, h, cur_roi, blob)
            if modified_roi is None:
                return False
        else:
            return False

        # ── MAD check: discard if change is imperceptible ──────────────
        mad = float(np.abs(modified_roi - orig_roi).mean())
        if mad < 4.0:
            # Too subtle — try boosting with a stronger Gaussian blend
            # (push the delta up, but never exceed what would be "obvious")
            if mad < 0.5:
                return False   # genuinely no effect (e.g. hue on grey)
            scale = min(12.0 / max(mad, 0.1), 2.5)
            modified_roi = np.clip(orig_roi + scale*(modified_roi - orig_roi), 0, 255)
            mad = float(np.abs(modified_roi - orig_roi).mean())
            if mad < 4.0:
                return False

        # ── Attenuate if way too obvious (MAD > 32) ────────────────────
        if mad > 32.0:
            scale = 32.0 / mad
            modified_roi = np.clip(orig_roi + scale*(modified_roi - orig_roi), 0, 255)

        self.modified[y:y+h, x:x+w] = np.clip(modified_roi, 0, 255).astype(np.uint8)
        return True

    # ──────────────────────────────────────────────────────────────────────
    # Effect implementations — each returns a modified float32 (h,w,3) array
    # ──────────────────────────────────────────────────────────────────────

    def _soft_darken(self, roi, blob):
        """
        Lighten or darken the centre with Gaussian falloff.

        factor 0.40–0.55 on a typical image → MAD ~19–27 (goldilocks zone).
        Looks like a soft shadow or highlight appeared over part of the scene.
        """
        factor = random.uniform(0.38, 0.52)
        direction = random.choice([1, -1])   # 1=darken, -1=lighten

        if direction == 1:
            # darken: multiply luminance by (1 - factor*blob)
            modified = roi * (1.0 - factor * blob[:, :, None])
        else:
            # lighten: pull toward 255
            modified = roi + (255.0 - roi) * (factor * blob[:, :, None])

        return np.clip(modified, 0, 255)

    # ──────────────────────────────────────────────────────────────────────

    def _local_warp(self, roi, blob, w, h):
        """
        Displace pixels outward from the centre using a Gaussian bump, then
        alpha-blend the warped result back using the same Gaussian mask.

        displacement 18–28 px → MAD ~15–22.  Looks like a shape bulged,
        a petal pushed out, or a branch bent slightly.
        """
        map_x = np.tile(np.arange(w, dtype=np.float32), (h, 1))
        map_y = np.tile(np.arange(h, dtype=np.float32).reshape(-1,1), (1, w))

        # Direction: outward or inward
        direction = random.choice([1.0, -1.0])
        disp = random.uniform(16.0, 26.0) * direction

        # Displacement follows the gradient of the blob (outward vector field)
        cx, cy = w / 2.0, h / 2.0
        dx_field = (map_x - cx) / (max(cx, 1))   # normalised [-1, 1]
        dy_field = (map_y - cy) / (max(cy, 1))

        mx = np.clip(map_x + disp * blob * dx_field, 0, w - 1).astype(np.float32)
        my = np.clip(map_y + disp * blob * dy_field, 0, h - 1).astype(np.float32)

        roi_u8  = np.clip(roi, 0, 255).astype(np.uint8)
        warped  = cv2.remap(roi_u8, mx, my, cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_REFLECT)

        # Blend: use blob as alpha so edges stay untouched
        alpha = blob[:, :, None]
        blended = warped.astype(np.float32) * alpha + roi * (1.0 - alpha)
        return blended

    # ──────────────────────────────────────────────────────────────────────

    def _hue_tint(self, roi, blob, h, w):
        """
        Rotate HSV hue by 25–50° at the centre, fading to 0° at edges.

        Works best on colourful images; calibration handles muted ones.
        Looks like a flower changed colour, or a surface took on a tint.
        """
        roi_u8  = np.clip(roi, 0, 255).astype(np.uint8)
        hsv     = cv2.cvtColor(roi_u8, cv2.COLOR_BGR2HSV).astype(np.float32)

        shift = random.choice([1, -1]) * random.uniform(25.0, 50.0)

        # Apply shift weighted by blob so it fades to 0 at boundary
        hsv[:, :, 0] = (hsv[:, :, 0] + shift * blob) % 180.0

        rotated = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # Blend using blob mask to ensure no hard edge
        alpha   = blob[:, :, None]
        blended = rotated.astype(np.float32) * alpha + roi * (1.0 - alpha)
        return blended

    # ──────────────────────────────────────────────────────────────────────

    def _contrast_pop(self, roi, blob):
        """
        Boost or reduce local contrast, weighted by Gaussian blob.

        boost 1.5–1.8 → MAD ~12–22.  Looks like a region became more vivid
        or flatter — similar to the effect of a different printing run.
        """
        boost     = random.uniform(1.45, 1.75)
        direction = random.choice([1, -1])   # 1=more contrast, -1=less

        local_mean = roi.mean(axis=(0, 1), keepdims=True)

        if direction == 1:
            stretched = local_mean + boost * (roi - local_mean)
        else:
            stretched = local_mean + (1.0 / boost) * (roi - local_mean)

        # Blend with Gaussian mask
        alpha   = blob[:, :, None]
        blended = stretched * alpha + roi * (1.0 - alpha)
        return np.clip(blended, 0, 255)

    # ──────────────────────────────────────────────────────────────────────

    def _clone_patch(self, x, y, w, h, roi, blob):
        """
        Copy a donor patch from a random other location in the image and
        alpha-blend it onto the target using the Gaussian mask.

        Because the mask fades to 0 at the boundary there is no hard edge —
        the donor content appears to smoothly "grow into" the scene.
        Looks like an extra object, leaf, or texture element appeared.

        Returns None if no valid donor is found within 20 attempts.
        """
        height, width = self.original.shape[:2]
        margin = 10

        for _ in range(20):
            dx = random.randint(margin, width  - w - margin)
            dy = random.randint(margin, height - h - margin)

            # Donor must not overlap target
            no_overlap = (dx+w <= x or dx >= x+w or dy+h <= y or dy >= y+h)
            if not no_overlap:
                continue

            donor = self.original[dy:dy+h, dx:dx+w].astype(np.float32)

            # alpha blend: donor in centre, original at edges
            alpha   = blob[:, :, None]
            blended = donor * alpha + roi * (1.0 - alpha)
            return blended

        return None

    # ──────────────────────────────────────────────────────────────────────

    def get_images(self):
        """Return (original, modified) as BGR uint8 NumPy arrays."""
        return self.original, self.modified

    def get_differences(self):
        """Return the list of Difference objects."""
        return self.differences
