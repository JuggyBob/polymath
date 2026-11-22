# C++ repair v3 (8/10)

String-keyed hash map with raw pointers, open addressing, tombstones, rehash
thresholds, plus a rule-of-three owned buffer. Fixed header. Visible tests fail
(feedback available); hidden tests cover the rest of the contracts.

Compile: `cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp`

Score: `python <REPO>\repair\cpp\v3\_grader\score.py --fixture <REPO>\repair\cpp\v3 --solution <dir>`
