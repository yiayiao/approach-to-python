#!/usr/bin/env python
# coding=utf-8

def bubble_sort(arr):
    for i in range(len(arr), 0, -1):
        for j in range(1, i):
            if arr[j - 1] > arr[j]:
                arr[j - 1], arr[j] = arr[j], arr[j - 1]

arr = [34, 6, 6756, 34, 324, 4543, 123]
bubble_sort(arr)
print arr
