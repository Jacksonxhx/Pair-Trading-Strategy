import statsmodels.api as sm
import pandas as pd


class RegressionModel:
    """
    Regression Model to fit the price data and find the best model
    """
    def __init__(self, training_data):
        self.training_data = training_data
        self.hedge_ratio = None
        self.alpha = None

    def fit(self):
        # TODO:(parameter optimization) 可以尝试更多不一样的regression模型找最佳
        y = self.training_data['GLD']
        X = self.training_data['GDX']
        X = sm.add_constant(X)
        # Linear regression
        model = sm.OLS(y, X).fit()
        self.alpha = model.params['const']
        self.hedge_ratio = model.params['GDX']
        return self.hedge_ratio, self.alpha

