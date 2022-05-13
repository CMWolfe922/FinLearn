from src.getter import Get, stock_chunks
from src.pricehistory import price_history
from src.fundamentals import fundamental
from src.quotes import Quote
from loguru import logger
from models.mysql_db import insert_quote_and_fundamental_data_mysql, connection_uri, marketdata_db, _select_symbols
import pandas as pd
import os
import time


# CREATE THE LOGGER FOR THIS SCRIPT:
log_path = str(os.path.pardir) + '/logs/'
base_fmt = "[{time:YYYY-MM-DD at HH:mm:ss}]|[{name}-<lvl>{message}</lvl>]"
logger.add(log_path+"main.log", rotation="5 MB",
           colorize=True, enqueue=True, catch=True)

# Select Symbols
stocks = _select_symbols()

# create a Get object
get = Get()

# Create Quote object
quote = Quote(stocks=stocks)

if __name__ == '__main__':
    logger.info("[+] Main Script Started")
    # time main file
    s = time.time()

    # =========================================================================== #
    # STEP 1: GET THE QUOTE AND FUNDAMENTAL DATA AND INSERT TO DATABASE
    # =========================================================================== #
    # Get the quote data using stock_chunks
    logger.info("[-] Getting Quote Data")
    quote_data = pd.concat([quote.data(each) for each in stock_chunks])
    logger.info("[+] Quote Data Received")

    # Get the fundamental data using stock_chunks
    logger.info("[-] Getting Fundamental Data")
    fundamental_data = pd.concat([fundamental.data(each)
                                 for each in stock_chunks])
    logger.info("[+] Fundamental Data Received")

    # create the marketdata database engine:
    engine = connection_uri + '/' + marketdata_db
    logger.info("[+] Database engine created")

    # insert the quote and fundamental data into mysql db
    logger.info("[-] Starting insert_quote_and_fundamental_data")
    insert_quote_and_fundamental_data_mysql(
        quote_data, fundamental_data, engine)
    logger.info("[+] insert_quote_and_fundamental_data Finished")

    # =========================================================================== #
    # STEP 2: EXECUTE MAIN PRICE HISTORY METHOD TO INSERT ALL PRICE DATA
    # =========================================================================== #
    # logger.info("[-] Starting price_history.execute_main()")
    # price_history.execute_main()
    # logger.info("[+] Finished price_history.execute_main()")
    # =========================================================================== #

    e = time.time()
    mins = (e - s) / 60
    logger.info(
        "[+] Main Script finished in {} minutes -", mins)
