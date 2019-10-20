import re
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as pl
import QuantLib as ql

# utility class for different QuantLib type conversions 
class Convert():
    
    # convert date string ('yyyy-mm-dd') to QuantLib Date object
    def to_date(s):
        monthDictionary = {
            '01': ql.January, '02': ql.February, '03': ql.March,
            '04': ql.April, '05': ql.May, '06': ql.June,
            '07': ql.July, '08': ql.August, '09': ql.September,
            '10': ql.October, '11': ql.November, '12': ql.December
        }
        arr = re.findall(r"[\w']+", s)
        return ql.Date(int(arr[2]), monthDictionary[arr[1]], int(arr[0]))
    
    # convert string to QuantLib businessdayconvention enumerator
    def to_businessDayConvention(s):
        if (s.upper() == 'FOLLOWING'): return ql.Following
        if (s.upper() == 'MODIFIEDFOLLOWING'): return ql.ModifiedFollowing
        if (s.upper() == 'PRECEDING'): return ql.Preceding
        if (s.upper() == 'MODIFIEDPRECEDING'): return ql.ModifiedPreceding
        if (s.upper() == 'UNADJUSTED'): return ql.Unadjusted
        
    # convert string to QuantLib calendar object
    def to_calendar(s):
        if (s.upper() == 'TARGET'): return ql.TARGET()
        if (s.upper() == 'UNITEDSTATES'): return ql.UnitedStates()
        if (s.upper() == 'UNITEDKINGDOM'): return ql.UnitedKingdom()
        # TODO: add new calendar here
        
    # convert string to QuantLib swap type enumerator
    def to_swapType(s):
        if (s.upper() == 'PAYER'): return ql.VanillaSwap.Payer
        if (s.upper() == 'RECEIVER'): return ql.VanillaSwap.Receiver
        
    # convert string to QuantLib frequency enumerator
    def to_frequency(s):
        if (s.upper() == 'DAILY'): return ql.Daily
        if (s.upper() == 'WEEKLY'): return ql.Weekly
        if (s.upper() == 'MONTHLY'): return ql.Monthly
        if (s.upper() == 'QUARTERLY'): return ql.Quarterly
        if (s.upper() == 'SEMIANNUAL'): return ql.Semiannual
        if (s.upper() == 'ANNUAL'): return ql.Annual

    # convert string to QuantLib date generation rule enumerator
    def to_dateGenerationRule(s):
        if (s.upper() == 'BACKWARD'): return ql.DateGeneration.Backward
        if (s.upper() == 'FORWARD'): return ql.DateGeneration.Forward
        # TODO: add new date generation rule here

    # convert string to QuantLib day counter object
    def to_dayCounter(s):
        if (s.upper() == 'ACTUAL360'): return ql.Actual360()
        if (s.upper() == 'ACTUAL365FIXED'): return ql.Actual365Fixed()
        if (s.upper() == 'ACTUALACTUAL'): return ql.ActualActual()
        if (s.upper() == 'ACTUAL365NOLEAP'): return ql.Actual365NoLeap()
        if (s.upper() == 'BUSINESS252'): return ql.Business252()
        if (s.upper() == 'ONEDAYCOUNTER'): return ql.OneDayCounter()
        if (s.upper() == 'SIMPLEDAYCOUNTER'): return ql.SimpleDayCounter()
        if (s.upper() == 'THIRTY360'): return ql.Thirty360()
        
    # convert string (ex.'USDLibor.3M') to QuantLib ibor index object
    # note: forwarding term structure has to be linked to index object separately
    def to_iborIndex(s):
        s = s.split('.')
        if(s[0].upper() == 'USDLIBOR'): return ql.USDLibor(ql.Period(s[1]))
        if(s[0].upper() == 'EURIBOR'): return ql.Euribor(ql.Period(s[1]))  

class VanillaSwap(object):
    
    def __init__(self, ID, swapType, nominal, startDate, maturityDate, fixedLegFrequency, 
        fixedLegCalendar, fixedLegConvention, fixedLegDateGenerationRule, fixedLegRate, fixedLegDayCount,
        fixedLegEndOfMonth, floatingLegFrequency, floatingLegCalendar, floatingLegConvention, 
        floatingLegDateGenerationRule, floatingLegSpread, floatingLegDayCount, 
        floatingLegEndOfMonth, floatingLegIborIndex):

        # create member data, convert all required QuantLib types
        self.ID = str(ID)
        self.swapType = Convert.to_swapType(swapType)
        self.nominal = float(nominal)
        self.startDate = Convert.to_date(startDate)
        self.maturityDate = Convert.to_date(maturityDate)
        self.fixedLegFrequency = ql.Period(Convert.to_frequency(fixedLegFrequency))
        self.fixedLegCalendar = Convert.to_calendar(fixedLegCalendar)
        self.fixedLegConvention = Convert.to_businessDayConvention(fixedLegConvention)
        self.fixedLegDateGenerationRule = Convert.to_dateGenerationRule(fixedLegDateGenerationRule)
        self.fixedLegRate = float(fixedLegRate)
        self.fixedLegDayCount = Convert.to_dayCounter(fixedLegDayCount)
        self.fixedLegEndOfMonth = bool(fixedLegEndOfMonth)
        self.floatingLegFrequency = ql.Period(Convert.to_frequency(floatingLegFrequency))
        self.floatingLegCalendar = Convert.to_calendar(floatingLegCalendar)
        self.floatingLegConvention = Convert.to_businessDayConvention(floatingLegConvention)
        self.floatingLegDateGenerationRule = Convert.to_dateGenerationRule(floatingLegDateGenerationRule)
        self.floatingLegSpread = float(floatingLegSpread)
        self.floatingLegDayCount = Convert.to_dayCounter(floatingLegDayCount)
        self.floatingLegEndOfMonth = bool(floatingLegEndOfMonth)
        self.floatingLegIborIndex = Convert.to_iborIndex(floatingLegIborIndex)

        # create fixed leg schedule
        self.fixedLegSchedule = ql.Schedule(
            self.startDate, 
            self.maturityDate,
            self.fixedLegFrequency, 
            self.fixedLegCalendar, 
            self.fixedLegConvention,
            self.fixedLegConvention,
            self.fixedLegDateGenerationRule,
            self.fixedLegEndOfMonth)
        
        # create floating leg schedule
        self.floatingLegSchedule = ql.Schedule(
            self.startDate, 
            self.maturityDate,
            self.floatingLegFrequency, 
            self.floatingLegCalendar, 
            self.floatingLegConvention,
            self.floatingLegConvention,
            self.floatingLegDateGenerationRule,
            self.floatingLegEndOfMonth)

    # NPV method used for specific calibration purposes
    # x = list of forward rates
    # args: 0 = list of forward dates, 1 = list of market rates        
    def NPV_calibration(self, x, args):
        # concatenate given market rates and given forward rates
        x = np.concatenate([args[1], x])
        
        # create QuantLib yield term structure object
        # from a given set of forward rates and dates
        curve = ql.YieldTermStructureHandle(ql.ForwardCurve(args[0], x, 
            self.floatingLegDayCount, self.floatingLegCalendar))        

        # set forwarding term structure to floating leg index
        self.floatingLegIborIndex = self.floatingLegIborIndex.clone(curve) 
        
        # create vanilla interest rate swap
        self.instrument = ql.VanillaSwap(
            self.swapType, 
            self.nominal, 
            self.fixedLegSchedule, 
            self.fixedLegRate, 
            self.fixedLegDayCount, 
            self.floatingLegSchedule,
            self.floatingLegIborIndex,
            self.floatingLegSpread, 
            self.floatingLegDayCount)
        
        # pair instrument with pricing engine, request PV
        self.instrument.setPricingEngine(ql.DiscountingSwapEngine(curve))
        return self.instrument.NPV()
    
    # NPV method used for general pricing purposes
    def NPV(self, yieldTermStructureHandle, floatingLegIborIndex):
        # set forwarding term structure to floating leg index
        self.floatingLegIborIndex = floatingLegIborIndex.clone(yieldTermStructureHandle)
        
        # create vanilla interest rate swap
        self.instrument = ql.VanillaSwap(
            self.swapType, 
            self.nominal, 
            self.fixedLegSchedule, 
            self.fixedLegRate, 
            self.fixedLegDayCount, 
            self.floatingLegSchedule,
            self.floatingLegIborIndex,
            self.floatingLegSpread, 
            self.floatingLegDayCount)
        
        # pair instrument with pricing engine, request PV
        self.instrument.setPricingEngine(ql.DiscountingSwapEngine(yieldTermStructureHandle))
        return self.instrument.NPV()

# objective function calculates sum of squared errors of all decision variables
# x = list of forward rates
# args: 0 = list of market rates data, 1 = scaling factor
def ObjectiveFunction(x, args):
    # concatenate given market rates and forward rates
    x = np.concatenate([args[0], x])
    return np.sum(np.power(np.diff(x), 2) * args[1])

# dynamic data parts for set of vanilla swaps 
swapIDs = ['2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '9Y', '10Y', '12Y', '15Y', '20Y', '25Y', '30Y']
maturities = ['2010-02-08', '2011-02-07', '2012-02-06', '2013-02-06', '2014-02-06', '2015-02-06', '2016-02-08', 
    '2017-02-06', '2018-02-06', '2020-02-06', '2023-02-06', '2028-02-07', '2033-02-07', '2038-02-08']
swapRates = [0.02795, 0.03035, 0.03275, 0.03505, 0.03715, 0.03885, 0.04025, 0.04155, 0.04265, 0.04435, 
    0.04615, 0.04755, 0.04805, 0.04815]

# create vanilla swap transaction objects into list
swaps = [VanillaSwap(swapID, 'Payer', 1000000, '2008-02-06', maturity, 'Annual', 
    'Target', 'ModifiedFollowing', 'Backward', swapRate, 'Actual360', False, 'Quarterly', 
    'Target', 'ModifiedFollowing', 'Backward', 0.0, 'Actual360', False, 'USDLibor.3M')
    for swapID, maturity, swapRate in zip(swapIDs, maturities, swapRates)]

# take initial forward rates from market data, set initial guesses and scaling factor for objective function
initialMarketData = np.array([0.03145, 0.0279275, 0.0253077, 0.0249374])
initialForwardGuesses = np.full(117, 0.02)
scalingFactor = 1000000.0

# create relevant QuantLib dates
today = ql.Date(4, 2, 2008)
ql.Settings.instance().evaluationDate = today  
settlementDate = ql.TARGET().advance(today, ql.Period(2, ql.Days))

# create set of dates for forward curve
dates = list(ql.Schedule(settlementDate, ql.Date(6, 2, 2038), ql.Period(ql.Quarterly), ql.TARGET(),
    ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Backward, False))

# create constraints for optimization model
swapConstraints = tuple([{'type': 'eq', 'fun': swap.NPV_calibration, 'args': [[dates, initialMarketData]]} for swap in swaps])

# create and execute scipy minimization model
model = opt.minimize(ObjectiveFunction, initialForwardGuesses, args = ([initialMarketData, scalingFactor]), 
    method = 'SLSQP', options = {'maxiter': 500}, constraints = swapConstraints)

# extract calibrated forward rates, create times and plot term structure
forwards = np.concatenate([initialMarketData, model.x])
times = np.array([ql.Actual360().yearFraction(settlementDate, date) for date in dates])
pl.plot(times, forwards)
pl.show()

# create new QuantLib curve from calibrated forward rates, print discount factors
curve = ql.YieldTermStructureHandle(ql.ForwardCurve(dates, forwards, ql.Actual360(), ql.TARGET()))

# value initial set of vanilla swaps using new QuantLib valuation curve
# all swaps should be priced to zero at inception date
for swap in swaps:
    index = ql.USDLibor(ql.Period(3, ql.Months), curve)
    pv = swap.NPV(curve, index)
    print(swap.ID, '{0:.5f}'.format(pv))
