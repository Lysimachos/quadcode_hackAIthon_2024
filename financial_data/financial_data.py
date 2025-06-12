from datetime import datetime, timedelta

import yfinance as yf
import pandas as pd


class FinancialStatementsAnalysis:
    def __init__(self, stock_symbol, period='yearly'):
        self.stock_symbol = stock_symbol
        self.period = period
        self.stock = yf.Ticker(stock_symbol)

    def _get_financial_data(self):
        if self.period == 'quarterly':
            return self.stock.quarterly_financials.transpose()
        else:
            return self.stock.financials.transpose()

    def _get_balance_sheet(self):
        if self.period == 'quarterly':
            return self.stock.quarterly_balance_sheet.transpose()
        else:
            return self.stock.balance_sheet.transpose()

    def _get_cashflow(self):
        if self.period == 'quarterly':
            return self.stock.quarterly_cashflow.transpose()
        else:
            return self.stock.cashflow.transpose()

    def get_historical_prices(self,past_years=3):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=past_years * 365)
        daily_close_prices = self.stock.history(start=start_date, end=end_date)
        return daily_close_prices

    def get_current_capitalization(self):
        return self.stock.info['marketCap']

    def get_recommendations(self):
        return self.stock.recommendations

    def get_financial_ratios(self):
        income_statement = self._get_financial_data()
        balance_sheet = self._get_balance_sheet()
        cashflow = self._get_cashflow()

        ratios = pd.DataFrame()

        # Efficiency Ratios
        ratios['A1'] = income_statement['EBIT'] / balance_sheet['Total Assets']
        ratios['A2'] = income_statement['Net Income From Continuing Operation Net Minority Interest'] / balance_sheet[
            'Stockholders Equity']
        ratios['A3'] = income_statement['Gross Profit'] / balance_sheet['Total Assets']
        ratios['A4'] = income_statement['Net Income'] / income_statement['Gross Profit']

        # Solvency Ratios
        ratios['B1'] = balance_sheet['Current Liabilities'] / balance_sheet[
            'Total Assets']
        ratios['B2'] = balance_sheet['Total Liabilities Net Minority Interest'] / balance_sheet['Total Assets']
        ratios['B3'] = balance_sheet['Long Term Debt'] / (
                    balance_sheet['Long Term Debt'] + balance_sheet['Stockholders Equity'])
        ratios['B4'] = balance_sheet['Current Assets'] / balance_sheet[
            'Current Liabilities']
        ratios['B5'] = (balance_sheet['Current Assets'] - balance_sheet['Inventory']) / balance_sheet[
                                                                       'Current Liabilities']

        # Management Performance Ratios
        ratios['C1'] = income_statement['Interest Expense'] / income_statement[
            'Total Revenue']
        ratios['C2'] = income_statement['Selling General And Administration'] / \
                                                             income_statement['Total Revenue']
        ratios['C3'] = (balance_sheet['Receivables'] * 365) / income_statement['Total Revenue']
        ratios['C4'] = (balance_sheet['Current Liabilities'] * 365) / \
                                                        income_statement['Cost Of Revenue']
        ratios['C5'] = (balance_sheet['Inventory'] * 365) / income_statement['Cost Of Revenue']

        return ratios

    def get_financial_ratios_definition(self):
        financial_ratios = {
                "A1": "EBIT / Total Assets",
                "A2": "Net Income / Net Worth",
                "A3": "Gross Profit / Total Assets",
                "A4": "Net Income / Gross Profit",
                "B1": "Current Liabilities / Total Assets",
                "B2": "Total Liabilities / Total assets",
                "B3": "Long Term Liabilities / (Long Term Liabilities + Net Worth)",
                "B4": "Quick Assets / Current Liabilities",
                "B5": "(Quick Assets-Inventories) / Current Liabilities",
                "C1": "Financial expense / Total revenue",
                "C2": "General and Administrative / Total revenue",
                "C3": "Demands / Average revenue",
                "C4": "Current Liabilities / Average revenue",
                "C5": "Inventories / Average revenue"
            }
        return financial_ratios


if __name__ == '__main__':
    stock_ratios = FinancialStatementsAnalysis('AAPL', 'quarterly')
    print(stock_ratios.get_ratios())