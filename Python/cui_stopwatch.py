import time
minutes = 10
for m in range(minutes):
    print(f'\n{m}:'
          + ''.join([' ' for _ in range(9)])
          .join([''] + [str(s) for s in range(1, 7)]),
          end='')
    for s in range(1, 61):
        time.sleep(1)
        print(f'\r{m}:'+ ''.join('#' for _ in range(s)), end='')
