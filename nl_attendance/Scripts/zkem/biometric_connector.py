# -*- coding: utf-8 -*-

import sys, os, time
import pytz
import win32com.client
import win32api
import win32event
import pythoncom
import xmlrpclib
import csv
from datetime import datetime, timedelta
from threading import Thread

threadlist = dict()

biometric_log = '/opt/zkem/biometric.log'
server_configuration = '/opt/zkem/server.csv'
attendance_server = "/opt/zkem/attendance.csv"

try:
    server_IP = ''
    server_PORT = ''
    server_DB = ''
    server_USER = ''
    server_PASSWORD = ''
    biometric_IP = ''
    biometric_TZ = ''
    server_url = ''
    server_configuration_file = (os.path.getsize(server_configuration))
    if server_configuration_file:
        server_configuration_txt = open(server_configuration, 'r')
        for data in csv.reader(server_configuration_txt):
            server_IP = data[0]
            server_PORT = data[1]
            server_DB = data[2]
            server_USER = data[3]
            server_PASSWORD = data[4]
            biometric_TZ = data[5]
            biometric_IP = data[6]
            server_url = data[8]
            if biometric_IP:
                input_code = 1
                print ('Biometric Device IP : ' + str(biometric_IP))
                # with open(biometric_log, 'a+') as the_file:
                #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Biometric Device IP : '+str(biometric_IP)+'\n' +' Biometric Device Timezone: '+str(biometric_TZ)+'\n'+' Server IP : '+str(server_IP)+'\n'+' Server Port : '+str(server_PORT)+'\n'+' Server Database : '+str(server_DB)+'\n'+' Admin User : '+str(server_USER)+'\n'+' Admin User Password : '+str(server_PASSWORD)+'\n')
            else:
                print('Biometric Device Fail to connect')
                # with open(biometric_log, 'a+') as the_file:
                #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Biometric Device Fail to connect'+'\n')
    else:
        print('Biometric Device Fail to connect')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Biometric Device Fail to connect'+'\n')
except:
    pass

def UTC2IST():
    timezone = pytz.timezone(biometric_TZ)
    utc_date = datetime.utcnow()
    utc_datetime = utc_date.replace(tzinfo=pytz.utc).astimezone(timezone)
    utc_datetime_strr = timezone.normalize(utc_datetime)
    return utc_datetime_strr

class ZkEvents:
    def __init__(self):
        self.event = win32event.CreateEvent(None, 0, 0, None)
        thread = win32api.GetCurrentThreadId()
        print ('Thread ' + str(thread) + '\n')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Thread '+str(thread)+'\n')
        self.testid = threadlist[thread]
        print ('Thread Connected For ID  ' + str(self.testid) + '\n')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Thread Connected For ID  '+str(self.testid)+'\n')

    def OnFinger(self):
        print ('Finger Punch \n')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Finger punch '+'\n')

    def OnVerify(self, user):
        if user == -1:
            print  ('Wrong Finger Punch \n')
            # with open(biometric_log, 'a+') as the_file:
            #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): WRONG FINGER '+'\n')
        else:
            print ('Correct User ID \n')
            # with open(biometric_log, 'a+') as the_file:
            #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): CORRECT USER ID',user+'\n')

    def OnAttTransactionEx(self, sEnrollNumber, iIsInValid, iAttState, iVerifyMethod, iYear, iMonth, iDay,iHour,iMinute,iSecond,iWorkCode):
        user = sEnrollNumber
        valid = iIsInValid
        state = iAttState
        print ("@@@@@   iAttState =====", state)
        print ("@@@@@   iYear =====", iYear)
        verify = iVerifyMethod
        workcode = iWorkCode
        datetime_str = str(iYear) + '-' + str(iMonth) + '-' + str(iDay) + ' ' + str(iHour) + ':' + str(iMinute) + ':' + str(iSecond)
        if datetime_str == '2000-0-0 0:0:0':
            with open(biometric_log, 'a+') as the_file:
                the_file.write('(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): wrong time '+'\n')
        else:
            datetime_input = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            tz = pytz.timezone(biometric_TZ)  # used Static timezone
            tz_datetime = tz.localize(datetime_input)
            utc_datetime = tz_datetime.astimezone(pytz.utc)
            utc_no_tz = utc_datetime.replace(tzinfo=None)
            RT_Attendance(user, valid, state, verify, workcode, utc_no_tz)

    def OnConnected(self):
        print ('Connected')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Connected' +'\n')

    def OnDisConnected(self):
        print ('Dis-Connected')
        # with open(biometric_log, 'a+') as the_file:
        #     the_file.write('('+UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Disconnected' +'\n')

def RT_Attendance(user, valid, state, verify, workcode, utc_no_tz):
    connection = 0
    print ("@@@@@  VALID=====", valid, user)
    print ("@@@@@  STATE=====", state)

    if state == 1:
        action = "check_out"
    elif state == 0:
        action = "check_in"
    elif state == 5:
        action = "over_time_out"
    else:
        action = "Over_time_in"
    try:
        server_user = server_USER
        server_db = server_DB
        server_password = server_PASSWORD

        sock = xmlrpclib.ServerProxy(str(server_url) +'/xmlrpc/common')
        uid = sock.login(server_db, server_user, server_password)

        sock = xmlrpclib.ServerProxy(str(server_url) +'/xmlrpc/object')

    except Exception as e:
        connection = + 1
        print ("@@@@@ Exception=====", e)
        pass
    if connection == 0:
        domain = [('fingerprint_id', '=', str(user))]
        if sock.execute(server_db, uid, server_password, 'hr.employee', 'search', domain):
            employees = sock.execute(server_db, uid, server_password, 'hr.employee', 'search', domain)
            print(">>>>>>>>>> employee found", employees)
            with open(biometric_log, 'a+') as the_file:
                msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): Online odoo Server -- Biometric id: '+ str(user)
                the_file.write(msg +'\n')
                sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
            employee = False
            if employees:
                employee = employees[0]
                attendance = (sock.execute(server_db, uid, server_password, 'hr.attendance', 'search', [('employee_id', '=', employee)]))
                login = datetime.strptime(str(utc_no_tz), "%Y-%m-%d %H:%M:%S")
                if attendance:
                    attendance_ids = sock.execute(server_db, uid, server_password, 'hr.attendance', 'read', max(attendance), ['employee_id', 'check_in', 'check_out'])
                    print ("ALREADY HAS ATTENDANCE WITH IDS=====", attendance_ids)
                    login_now = login.date()
                    for i in attendance_ids:
                        get_value = " "
                        if i.get('check_in'):
                            get_value = i.get('check_in')
                        elif i.get('check_out'):
                            get_value = i.get('check_out')
                        checkin = datetime.strptime(get_value, "%Y-%m-%d %H:%M:%S").date()
                        print(">>>>>>>>>>>>>>>>>>>>>.lgoin now", login_now)
                        if checkin == login_now:
                            print(">>>>>>>>>>>>>>>>>>>>>>>. has an attendance in same day so update checkout")
                            sock.execute(server_db, uid, server_password, 'hr.attendance', 'write', i.get('id'), {'check_out': str(utc_no_tz)})
                        else:
                            print(">>>>>>>>>>>>>>>>>>>>>>>.create attendance for next day")
                            sock.execute(server_db, uid, server_password, 'hr.attendance', 'create', {'employee_id': employee, 'check_in': str(utc_no_tz)})

                else:
                    print ("FIRST TIME ATTENDANCE")
                    sock.execute(server_db, uid, server_password, 'hr.attendance', 'create', {'employee_id': employee, 'check_in': str(utc_no_tz)})

            else:
                with open(biometric_log, 'a+') as the_file:
                    msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): Online odoo Server -- Wrong User '+ str(user)+ 'Try to gain access of server.'
                    the_file.write(msg +'\n')
                    sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
    else:
        print ("@@@@@ NOT CONNECTON =====")
        attendance_server_txt = open(attendance_server, 'a+')
        fieldnames = ['id', 'datetime', 'checkin/checkout']
        offline_header = csv.DictWriter(attendance_server_txt, fieldnames=fieldnames, lineterminator='\n')
        offline_header.writeheader
        if offline_header:
            offline_header.writerow({'id': user, 'datetime': str(utc_no_tz), 'checkin/checkout': str(action)})
            with open(biometric_log, 'a+') as the_file:
                the_file.write('(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): Offline odoo Server --   Biometric id: '+ str(user)+' Datetime :'+str(utc_no_tz) +' action : '+str(action) +'\n')
        attendance_server_txt.close()

def WaitWhileProcessingMessages(event, timeout=5):
    start = time.clock()
    while True:
        rc = win32event.MsgWaitForMultipleObjects((event,), 0, 40, win32event.QS_ALLEVENTS) # 250,
        if rc == win32event.WAIT_OBJECT_0:
            return True
        if (time.clock() - start) > timeout:
            return False
        pythoncom.PumpWaitingMessages()

def TestZkEvents(ip, testid):
    try:
        server_user = server_USER
        server_db = server_DB
        server_password = server_PASSWORD

        sock = xmlrpclib.ServerProxy(str(server_url) +'/xmlrpc/common')
        uid = sock.login(server_db, server_user, server_password)

        sock = xmlrpclib.ServerProxy(str(server_url) +'/xmlrpc/object')

        thread = win32api.GetCurrentThreadId()
        with open(biometric_log, 'a+') as the_file:
            msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'):TestZkEvents created ZK object on thread : ' +str(thread)
            the_file.write(msg +'\n')
            sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
        threadlist[thread] = testid
        pythoncom.CoInitialize()
        zk = win32com.client.DispatchWithEvents("zkemkeeper.ZKEM", ZkEvents)
        print ("@@@@@ ZK =====", zk)
        try:
            if zk.Connect_Net(ip, 4370):
                with open(biometric_log, 'a+') as the_file:
                    msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): Biometric connection '+str(ip)+' Successfull'
                    the_file.write(msg +'\n')
                    sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
                while True:
                    try:
                        if not zk.RegEvent(1, 65535):
                            try:
                                zk.Connect_Net(ip, 4370)
                                zk.RegEvent(1, 65535)
                                with open(biometric_log, 'a+') as the_file:
                                    msg = '(' + UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Reconnect Biometric device : '+str(ip)+' Successfull'
                                    the_file.write(msg +'\n')
                                    sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
                            except:
                                with open(biometric_log, 'a+') as the_file:
                                    msg = '(' + UTC2IST().strftime("%d-%m-%Y")+' '+UTC2IST().strftime("%H:%M:%S")+'): Fail to connect Please check hardware status '+str(ip)+' Successfull'
                                    the_file.write(msg +'\n')
                                    sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
                                pass

                    except pythoncom.com_error, details:
                        with open(biometric_log, 'a+') as the_file:
                            msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'):  Warning - could not open the test HTML file'+str(details)
                            the_file.write(msg +'\n')
                            sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})


                    if not WaitWhileProcessingMessages(zk.event):
                        WaitWhileProc = 'ip'
            else:
                with open(biometric_log, 'a+') as the_file:
                    msg = '(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'):  Connection with device Failed'
                    the_file.write(msg +'\n')
                    sock.execute(server_db, uid, server_password, 'hr.attendance.logs', 'create', {'name': msg, 'ip_address': str(biometric_IP)})
        except:
            pass

        zk = None

    except Exception as e:
        with open(biometric_log, 'a+') as the_file:
            the_file.write('(' + UTC2IST().strftime("%d-%m-%Y") + ' ' + UTC2IST().strftime("%H:%M:%S")+'): Offline odoo Server' +'\n')
        print ("@@@@@ Exception=====", e)
        pass

if __name__ == '__main__':
    try:
        # A Minimal Example with Function Call
        TERMINAL1 = Thread(target=TestZkEvents, args=(biometric_IP, input_code))
        TERMINAL1.start()
        # TERMINAL2 = Thread(target=TestZkEvents, args=("10.42.0.18", input_code))
        # TERMINAL2.start()
    except:
        pass
