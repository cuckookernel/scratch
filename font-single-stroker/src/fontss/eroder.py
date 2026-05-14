import numpy as np
from numpy.typing import NDArray


def _count_components_3x3(m: NDArray[np.bool_]) -> int:
    """Calculates the number of 8-connected foreground components in a 3x3 binary matrix."""
    visited = np.zeros((3, 3), dtype=bool)
    count = 0
    for r in range(3):
        for c in range(3):
            if m[r, c] and not visited[r, c]:
                count += 1
                stack = [(r, c)]
                visited[r, c] = True
                while stack:
                    curr_r, curr_c = stack.pop()
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 <= nr < 3 and 0 <= nc < 3:  # noqa: PLR2004
                                if m[nr, nc] and not visited[nr, nc]:
                                    visited[nr, nc] = True
                                    stack.append((nr, nc))
    return count


def _generate_thinning_lut() -> NDArray[np.bool_]:
    """
    Precomputes a 256-entry Look-Up Table for topological erosion.
    Each index represents 8 neighbors (center pixel at (1,1) is assumed True).

    Rules for 'turning off' (True in LUT):
    1. Connectivity: Don't turn off if the number of connected components would change.
    2. Isolated: Don't turn off if it's the only foreground pixel in 3x3.
    3. Endpoint: Don't turn off if it has only one neighbor (is a line endpoint).
    """
    lut = np.zeros(256, dtype=bool)
    for i in range(256):
        # Build 3x3 matrix from bits (0-indexed bits for neighbors)
        # Neighbor layout:
        # 0 1 2
        # 3 C 4
        # 5 6 7
        m = np.zeros((3, 3), dtype=bool)
        m[0, 0] = bool(i & (1 << 0))
        m[0, 1] = bool(i & (1 << 1))
        m[0, 2] = bool(i & (1 << 2))
        m[1, 0] = bool(i & (1 << 3))
        m[1, 1] = True  # Center foreground pixel
        m[1, 2] = bool(i & (1 << 4))
        m[2, 0] = bool(i & (1 << 5))
        m[2, 1] = bool(i & (1 << 6))
        m[2, 2] = bool(i & (1 << 7))

        num_fg = np.sum(m)

        # Rule 2: Matrix contains just the center foreground pixel (num_fg == 1)
        # Rule 3: Matrix contains center and only one other pixel (num_fg == 2)
        if num_fg <= 2:  # noqa: PLR2004
            lut[i] = False
            continue

        # Rule 1: Connectivity check (8-connectivity)
        cc_before = _count_components_3x3(m)
        m[1, 1] = False
        cc_after = _count_components_3x3(m)

        # "Should be turned off" is True if connectivity is preserved
        lut[i] = (cc_before == cc_after)

    return lut


# Global LUT precomputed at module load
_THINNING_LUT = _generate_thinning_lut()


def _process_pixel(r: int, c: int, res: NDArray[np.bool_], padded: NDArray[np.bool_]) -> bool:
    """Checks if a single pixel should be turned off and updates state if so."""
    if not res[r, c]:
        return False

    # Extract 8 neighbors as bits for LUT index using the same order as LUT generation
    bits = 0
    # Map neighbors relative to (r,c) in res to (r+dr, c+dc) in padded
    # Offset is 0, 1, 2 for both rows and columns in the 3x3 window in padded
    for bit_idx, (dr, dc) in enumerate([(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]):
        if padded[r + dr, c + dc]:
            bits |= 1 << bit_idx

    if _THINNING_LUT[bits]:
        res[r, c] = False
        padded[r + 1, c + 1] = False
        return True
    return False


def erode_glyph(raster_glyph: NDArray[np.bool_]) -> NDArray[np.bool_]:
    """
    Iteratively erodes a binary raster glyph to a single-line skeleton while maintaining topology.

    It loops sequentially over foreground pixels and decides whether to turn them off
    based on a precomputed 256-entry LUT representing all possible 3x3 neighborhoods.
    """
    res = raster_glyph.copy()
    h, w = res.shape

    changed = True
    while changed:
        changed = False
        # Create a padded version to handle boundaries and provide neighborhood bits
        # Decisions are sequential: we update padded immediately for the next pixel.
        padded = np.pad(res, 1, mode="constant", constant_values=False)

        for r in range(h):
            for c in range(w):
                if _process_pixel(r, c, res, padded):
                    changed = True

    return res
