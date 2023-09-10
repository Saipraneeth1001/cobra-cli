import time
from image_reader import read_image, file_reader
from cobra_signals import my_trading_algo


if __name__ == "__main__":
    read_image()
    time.sleep(0.5)
    print("\n Analysing the stock data which you requested...")

    stocks = file_reader()

    for stock in stocks:
        my_trading_algo(str(stock))

    
