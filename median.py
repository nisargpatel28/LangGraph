from typing import List


def find_median_sorted_arrays(nums1: List[int], nums2: List[int]) -> float:
    """Find median of two sorted arrays in O(log(min(m,n))) time.

    This implements the standard binary-search-on-partition approach.

    Args:
        nums1: first sorted list
        nums2: second sorted list

    Returns:
        Median as float
    """
    # Ensure nums1 is the smaller array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    if m == 0:
        # Median of single array nums2
        mid = n // 2
        if n % 2 == 1:
            return float(nums2[mid])
        else:
            return (nums2[mid - 1] + nums2[mid]) / 2.0

    imin, imax, half_len = 0, m, (m + n + 1) // 2
    while imin <= imax:
        i = (imin + imax) // 2
        j = half_len - i

        if i < m and nums2[j - 1] > nums1[i]:
            # i is too small, must increase it
            imin = i + 1
        elif i > 0 and nums1[i - 1] > nums2[j]:
            # i is too big, must decrease it
            imax = i - 1
        else:
            # i is perfect
            if i == 0:
                max_of_left = nums2[j - 1]
            elif j == 0:
                max_of_left = nums1[i - 1]
            else:
                max_of_left = max(nums1[i - 1], nums2[j - 1])

            if (m + n) % 2 == 1:
                return float(max_of_left)

            if i == m:
                min_of_right = nums2[j]
            elif j == n:
                min_of_right = nums1[i]
            else:
                min_of_right = min(nums1[i], nums2[j])

            return (max_of_left + min_of_right) / 2.0


def _run_examples() -> None:
    examples = [
        (([1, 3], [2]), 2.0),
        (([1, 2], [3, 4]), 2.5),
        (([], [1]), 1.0),
        (([2], []), 2.0),
        (([0, 0], [0, 0]), 0.0),
        (([1, 2], [-1, 3]), 1.5),
        (([1, 3, 5], [2, 4, 6, 8]), 4.0),
    ]

    for (a, b), expected in examples:
        out = find_median_sorted_arrays(a, b)
        print(f"nums1={a}, nums2={b} -> median={out} (expected {expected})")


if __name__ == "__main__":
    _run_examples()


class Solution:
    """LeetCode-compatible wrapper class.

    Provides the method name expected by many online judges: `findMedianSortedArrays`.
    """

    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        return find_median_sorted_arrays(nums1, nums2)
