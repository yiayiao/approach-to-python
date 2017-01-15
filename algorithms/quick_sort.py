#!/usr/bin/env python
# coding=utf-8


def quick_sort(arr, p, r):
    if p < r:
        q = partition(arr, p, r)
        quick_sort(arr, p, q - 1)
        quick_sort(arr, q + 1, r)

def partition(arr, p, r):
    x = arr[r]
    i = p - 1
    for j in range(p, r + 1):
        if arr[j] < x:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1],arr[r] = arr[r], arr[i + 1]
    return i + 1

import random

def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list

if __name__=='__main__':
    arr = random_int_list(0, 20, 10)
    print arr
    quick_sort(arr, 0, len(arr) - 1)
    print arr
