#!/usr/bin/env python
# coding=utf-8

def merge(arr, p, q, r):
    arr1 = arr[p : q + 1]
    arr2 = arr[q + 1 : r + 1]
    i = j = 0

    for k in range(p, r + 1):
        if i < len(arr1) and (j == len(arr2) or arr1[i] < arr2[j]):
            arr[k] = arr1[i]
            i += 1
        else:
            arr[k] = arr2[j]
            j += 1
        
def merge_sort(arr, p, r):
    if p == r:
        return

    q = (p + r) / 2
    merge_sort(arr, p, q)
    merge_sort(arr, q + 1, r)
    merge(arr, p, q, r);

import random

def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list

arr = random_int_list(0, 20, 10);
print arr
merge_sort(arr, 0, len(arr) - 1)
print arr
