"""
================================================================================
Module: sorting_utils.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- Algorithm Design: Manual implementation of Bubble Sort
- Lists & Tuples: Working with lists of (word, count) tuples
- Nested Loops: Outer 'for' loop and inner 'for' loop
- Swapping Variables: Pythonic tuple unpacking (a, b = b, a)
- Conditionals & Flags: 'swapped' optimization boolean flag
- Time & Space Complexity Analysis: O(n²) vs O(n)
================================================================================
"""


def bubble_sort_frequencies(freq_items: list, descending: bool = True) -> tuple:
    """
    Demonstrates: Manual Bubble Sort implementation on a list of (word, count) tuples.

    Parameters:
    - freq_items: List of tuples, e.g., [('news', 12), ('report', 8), ('government', 10)]
    - descending: If True, sorts from highest frequency to lowest; if False, lowest to highest.

    Returns:
    - A tuple: (sorted_list, total_passes, total_comparisons, total_swaps)
    """
    # Create a shallow copy so we do not mutate the original input list
    items = list(freq_items)
    n = len(items)

    # Metrics to demonstrate algorithm mechanics in viva
    comparisons = 0
    swaps = 0
    passes_completed = 0

    # Outer loop: controls the number of passes
    for i in range(n):
        swapped = False
        passes_completed += 1

        # Inner loop: compares adjacent elements
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            comparisons += 1

            # Compare based on the frequency count (index 1 of tuple)
            # If counts are equal, sort alphabetically by word (index 0)
            count_j = items[j][1]
            count_next = items[j + 1][1]

            should_swap = False
            if descending:
                if count_j < count_next:
                    should_swap = True
                elif count_j == count_next and items[j][0] > items[j + 1][0]:
                    should_swap = True
            else:
                if count_j > count_next:
                    should_swap = True
                elif count_j == count_next and items[j][0] > items[j + 1][0]:
                    should_swap = True

            if should_swap:
                # Pythonic swap: a, b = b, a
                items[j], items[j + 1] = items[j + 1], items[j]
                swaps += 1
                swapped = True

        # Optimization: If no elements were swapped in this pass, list is already sorted!
        if not swapped:
            break

    return (items, passes_completed, comparisons, swaps)


def bubble_sort_words_alphabetical(words_list: list) -> list:
    """
    Demonstrates: Bubble Sort applied directly to a list of strings for alphabetical order.
    """
    words = list(words_list)
    n = len(words)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if words[j] > words[j + 1]:
                words[j], words[j + 1] = words[j + 1], words[j]
                swapped = True
        if not swapped:
            break

    return words


def get_bubble_sort_explanation(total_items: int, passes: int, comparisons: int, swaps: int) -> str:
    """
    Returns a clean, student-friendly explanation of Bubble Sort tailored for viva examination.
    """
    explanation = f"""
===============================================================================
                     BUBBLE SORT ALGORITHM EXPLANATION
===============================================================================

1. WHAT IS BUBBLE SORT?
   Bubble Sort is a simple comparison-based sorting algorithm. It works by
   repeatedly stepping through the list, comparing adjacent elements, and
   swapping them if they are in the wrong order. The pass through the list
   is repeated until no swaps are needed, meaning the list is fully sorted.

2. WHY DID WE USE IT HERE?
   - In our project, we sort word frequencies from HIGHEST to LOWEST.
   - It demonstrates that we understand how sorting works under the hood
     rather than relying blindly on Python's built-in sorted() function.
   - It is easy to visualize, trace, and explain during a project viva.

3. HOW DID IT PERFORM ON THIS DATA?
   - Total items sorted: {total_items}
   - Total passes completed: {passes}
   - Total comparisons performed: {comparisons}
   - Total swaps performed: {swaps}

4. TIME & SPACE COMPLEXITY:
   - Best Case:    O(n)      (Occurs when the list is already sorted;
                              our 'swapped' flag detects this in pass 1!)
   - Average Case: O(n²)     (Occurs when elements are in random order)
   - Worst Case:   O(n²)     (Occurs when elements are in reverse order)
   - Space:        O(1)      (In-place sorting; requires no extra memory)

5. KEY CODE MECHANISM:
   for i in range(n):
       for j in range(0, n - i - 1):
           if items[j][1] < items[j + 1][1]:
               items[j], items[j + 1] = items[j + 1], items[j]
===============================================================================
"""
    return explanation.strip()
