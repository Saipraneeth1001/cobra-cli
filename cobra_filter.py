def filter_rows(data, count):
    NEXT_COUNT = 10
    prev_close = data[count][1]['Close']
    # print("Buy signal for ", data[count][0])
    for i in range(2, NEXT_COUNT):
        if count + i < len(data):
            curr_close = data[count+i][1]['Close']
            pnl = curr_close - prev_close
            # print(data[count+i][0], curr_close, pnl)
            if pnl > 0:
                print(data[count][0], data[count+i][0], curr_close, pnl)
            