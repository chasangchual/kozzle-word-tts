#!/usr/bin/env python3
from kiwipiepy import Kiwi

kiwi = Kiwi()
tokens = kiwi.tokenize("나는 학교에 갔다. 친구와 점심을 먹었다.")

print("Token attributes:")
print(dir(tokens[0]))
print("\nFirst 3 tokens:")
for t in tokens[:5]:
    print(f"Token: {t}")
    print(f"Form: {t.form}")
    print(f"Tag: {t.tag}")
    print()
