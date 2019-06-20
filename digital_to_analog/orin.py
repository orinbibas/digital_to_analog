import easygui

def pre_run():
    msg = "Enter sensors details for each channel number, if no sensor is connected leave blank"
    title = "Sensors cofiguration"
    fieldNames = ["0","1","2","3","4","5","6","7"]
    fieldValues = []  # we start with blanks for the values
    fieldValues = easygui.multenterbox(msg,title, fieldNames)
    str_vals = ''
    actives = []
    for i in range(len(fieldValues)):
        if fieldValues[i] == '':
            pass
        else:
            str_vals += fieldNames[i]+'_'+fieldValues[i]+','
            actives.append((fieldNames[i],fieldValues[i]))
    
    return actives , str_vals
    
def assert_sensors(actives,str_vals):
    check = easygui.ccbox(msg=f'this are the active sensors and their serial number\n {actives} \n if any of the information is not correct please press cancel and start again',title='sensors info')
    if check == True:
        return str_vals
    else:
        pygame.quit()

if __name__ == "__main__":
    actives, str_vals = pre_run()
    assert_sensors(actives,str_vals)