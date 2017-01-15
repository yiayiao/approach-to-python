#!/usr/bin/env python
# coding=utf-8

def quick_sort2(arr, p, r):
    if p >= r:
        return
    k = arr[p]
    i = p
    j = r
    while i < j:
        while arr[j] >= k and i < j:
            j -= 1
        arr[i] = arr[j]
        while arr[i] <= k and i < j:
            i += 1
        arr[j] = arr[i]
    arr[i] = k
    quick_sort2(arr, p, i - 1)
    quick_sort2(arr, i + 1, r)

import random 

def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start < stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    int_list = []
    for i in range(length):
        int_list.append(random.randint(start, stop))
    return int_list

if __name__ == '__main__':
    arr = random_int_list(10, 100, 20)
    print arr
    quick_sort2(arr, 0, len(arr) - 1)
    print arr
