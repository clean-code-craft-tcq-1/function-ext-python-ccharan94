# =============================================================================
# ---------------------------------------------
# Battery Monitoring System:
# ---------------------------------------------    
# =============================================================================

#Declare global variables
CURRENT_BATTERYPACK   =   'Lithium'
LANGUAGE              =   'EN'
ALERTS                =    []

#Define multi language error messages
error_messages               = {'low_breach'  : { 'DE' : 'Untergrenze überschritten für ', 
                                                  'EN' : 'Lower Limit Breached for ' }   ,
                                'low_warning' : { 'DE' : 'Warnung vor Untergrenze für '  ,   
                                                  'EN' : 'Warning: Lower Limit approaching for '},
                                'high_breach' : { 'DE' : 'Obergrenze überschritten für '  , 
                                                  'EN' : 'Higher Limit Breached for ' }   ,
                                'high_warning': { 'DE' : 'Warnung vor höherer Grenze für ', 
                                                  'EN' : 'Warning: Higher Limit approaching for ' } }


#Declare operating threshold params for different battery packs
batteryThresholdParams = { 'Lithium' : 
                            {
                            'Temperature'  : { 'lower':  0   , 'upper': 45  },
                            'StateOfCharge': { 'lower': 20   , 'upper': 80  },
                            'ChargeRate'   : { 'lower': 0    , 'upper': 0.8 },
                            }, 
                                    
                         'NiMh' :   
                            {
                            'Temperature'  : { 'lower': -20  , 'upper': 40 },
                            'StateOfCharge': { 'lower':  20  , 'upper': 80  },
                            'ChargeRate'   : { 'lower': 0    , 'upper': 0.8 },
                            },   
                         }

def getBatteryThresholdLimit(batteryType):
    return batteryThresholdParams[batteryType]

#Check if Battery is working fine
def battery_is_ok(**kwargs):
  
  batteryLimits             = getBatteryThresholdLimit(CURRENT_BATTERYPACK)
    
  global BATTERY_CONDITION_ALL_OK
  BATTERY_CONDITION_ALL_OK  = True
  
  for criteria, criteriavalue in kwargs.items():
      lower,upper    = getBoundaryConditions(batteryLimits,criteria, criteriavalue)
      lower_status   = checkLowerLimitBreach(criteriavalue,lower,upper) 
      upper_status   = checkUpperLimitBreach(criteriavalue,upper)
      hasBreached    = checkBreaches(lower_status, upper_status)

      if hasBreached:
          BATTERY_CONDITION_ALL_OK = False
          global ALERTS
          ALERTS = setErrorMessages(upper_status, lower_status, criteria, criteriavalue)       
          
      printErrorMessages(ALERTS)
          
  return BATTERY_CONDITION_ALL_OK

def checkBreaches(lower_status, upper_status):
    if not ( upper_status == 'normal' and lower_status == 'normal'):
        return True
    else:
        return False
    

def setErrorMessages(upper_status, lower_status, criteria, criteriavalue):
     if upper_status != 'normal':
         status = upper_status
         error = { 'criteria': criteria, 'criteriavalue' : criteriavalue, 'status' : status}
         ALERTS.append(error)
     elif lower_status != 'normal':
         status = lower_status
         error = { 'criteria': criteria, 'criteriavalue' : criteriavalue, 'status' : status}
         ALERTS.append(error)
     return ALERTS
    

def printErrorMessages(ALERTS):
    for error in ALERTS:
        error_type = error['status']
        print ( error_messages[error_type][LANGUAGE] + error['criteria'] )
            
    if ALERTS.__len__ != 0:
        ALERTS.clear()

def getBoundaryConditions(batteryLimits,criteria, criteriavalue):
      upper = batteryLimits[criteria]['upper'] 
      lower = batteryLimits[criteria]['lower']
          
      return lower,upper 

def checkLowerLimitBreach(criteriavalue,lower,upper):
    if criteriavalue < lower:
        return 'low_breach'
    elif criteriavalue < lower + upper*0.05:
        return 'low_warning'
    else:
        return 'normal'

def checkUpperLimitBreach(criteriavalue,upper):
    if criteriavalue > upper:
        return 'high_breach'
    elif criteriavalue > upper*0.95:
        return 'high_warning'
    else:
        return 'normal'

         

if __name__ == '__main__':
    
 #Create boundary values for test - middle range, upper limit, lower limit
  temperature_limits = batteryThresholdParams[CURRENT_BATTERYPACK]['Temperature']
  soc_limits         = batteryThresholdParams[CURRENT_BATTERYPACK]['StateOfCharge']
  chargerate_limits  = batteryThresholdParams[CURRENT_BATTERYPACK]['ChargeRate']
  
  #middle range
  temp_middle_range        = ( temperature_limits['upper'] - temperature_limits['lower'] ) / 2
  soc_middle_range         = (         soc_limits['upper'] -         soc_limits['lower'] ) / 2
  chargerate_middle_range  = (  chargerate_limits['upper'] -  chargerate_limits['lower'] ) / 2
  
  #------------------------------------------------------
  #Generate dynamic testcases independent of battery type
  #------------------------------------------------------
  
  """Temperature Tests"""
  #Testcase for normal temperature working range 
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is True), 'Temperature Normal Range Test'
  #Testcase to check Upper limit breach for temperature
  assert(battery_is_ok(Temperature = temperature_limits['upper']+1, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is False), 'Temperature Upper Limit Breach'
  #Testcase to check Lower limit breach for temperature 
  assert(battery_is_ok(Temperature = temperature_limits['lower']-1, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is False), 'Temperature Lower Limit Breach'
  #Lower limit edge testcase for temperature
  assert(battery_is_ok(Temperature = temperature_limits['lower']+2, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is False), 'Temperature Lower Limit Warning'
  #Upper limit edge testcase for temperature
  assert(battery_is_ok(Temperature = temperature_limits['upper']-2, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is False), 'Temperature Upper Limit Warning'

  """State Of Charge Tests"""
  #Testcase for normal State of charge working range 
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range) is True), 'SOC Normal Range Test'
  #Testcase to check Upper limit breach for State of charge
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_limits['upper']+1, ChargeRate = chargerate_middle_range) is False), 'SOC Upper Limit Breach'
  #Testcase to check Lower limit breach for State of charge 
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_limits['lower']-1, ChargeRate = chargerate_middle_range) is False), 'SOC Lower Limit Breach'
  #Upper limit edge testcase for State of charge 
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_limits['upper']-2, ChargeRate = chargerate_middle_range) is False), 'SOC Upper Limit Edge Warning'
  #Lower limit edge testcase for State of charge
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_limits['lower']+2, ChargeRate = chargerate_middle_range) is False), 'SOC Lower Limit Edge Warning'

  """Charge Rate Tests"""
  #Testcase for normal Charge Rate working range 
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_middle_range ) is True), 'Charge Rate Range Test'
  #Testcase to check Upper limit breach for Charge Rate
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_limits['upper']+0.1) is False), 'Charge Upper Limit Breach'
  #Testcase to check lower limit breach for Charge Rate
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_limits['lower']-0.1) is False), 'Charge Lower Limit Breach'
  #Testcase to check Upper limit breach for Charge Rate
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_limits['upper']-0.02) is False), 'Charge Upper Limit Warning'
  #Testcase to check lower limit breach for Charge Rate
  assert(battery_is_ok(Temperature = temp_middle_range, StateOfCharge = soc_middle_range, ChargeRate = chargerate_limits['lower']+0.02) is False), 'Charge Lower Limit Warning'
 
