import serial
import timeit
import numpy as np




# time.sleep is unreliable
def wait (delay=0.2) :
    timeout = timeit.default_timer () + delay
    while (True) :
        if timeit.default_timer () > timeout :
            return
    return

def addCheckSum (data) : # data is a byte array
    checksum = sum (data)
    data.append (checksum % 256)
    return data

def Command_SetBaudRate (divisor) :
    command = bytearray ([0,0,0,divisor])
    return addCheckSum (command)

def Command_SendData (start_channel, words_requested,
                      upper=False, group=False):
    # should only call with int
    if not isinstance (start_channel, int) :
        raise TypeError ('StartChannelNotInt')
    if not isinstance (words_requested, int) :
        raise TypeError ('WordsRequestedNotInt')
    # need to verify that the arguments are in bounds
    if start_channel > 16383:
        raise ValueError ('StartChannelHigh')
    if start_channel < 0 :
        raise ValueError ('StartChannelLow')
    if words_requested > 1024 :
        raise ValueError ('WordsRequestedHigh')
    if words_requested < 1 :
        raise ValueError ('WordsRequestedLow')
    words_arg = words_requested - 1 # the MCA wants a number from 0-1023
    command_byte = 64 # lower
    if upper : command_byte += 2
    if group : command_byte += 16
    # lower command byte is 64 or 0x40 or 1000000
    # upper command byte is 66 or 0x42 or 1000010
    # lower group command byte is 80 or 0x50 or 1010000
    # upper group command byte is 82 or 0x52 or 1010010
    byte2 = start_channel % 256
    byte1 = start_channel // 256
    byte1 = byte1 << 2
    byte3 = words_arg % 256
    byte1 += words_arg // 256
    command = bytearray ([command_byte, byte1, byte2, byte3])
    return addCheckSum (command)
    
def Command_SendDataOld (start_channel, upper=False, group=False):
    # should only call with int
    if not isinstance (start_channel, int) :
        raise TypeError ('StartChannelNotInt')
    # need to verify that the arguments are in bounds
    if start_channel > 16383:
        raise ValueError ('StartChannelHigh')
    if start_channel < 0 :
        raise ValueError ('StartChannelLow')
    command_byte = 0 # SEND DATA AND CHECK SUM COMMAND
    n = 0 # lower
    if upper : n = 2
    if group : command_byte = 16 # SEND DATA, GROUP AND S/N COMMAND
    val = start_channel*4 + n
    byte1, byte2 = val.to_bytes(2, byteorder="big")
    byte3 = 0
    if group : byte3 = 1
    command = bytearray ([command_byte, byte1, byte2, byte3])
    return addCheckSum (command)
    
    
def Command_Control (flags, threshold) :
    # should check type of flags (needs to be 1 byte)
    if not isinstance (threshold, int) :
        raise TypeError ('ThresholdNotInt')
    if threshold < 0 :
        raise ValueError ('ThresholdLow')
    if threshold > 16383 :
        raise ValueError ('ThresholdHigh')
    command_byte = 1
    byte2 = threshold % 256 # lower byte
    byte3 = threshold // 256 # upper byte
    command = bytearray ([command_byte, flags, byte2, byte3])
    return addCheckSum (command)

# pick lock number zero to unlock and wipe (e.g. in case you don't know lock#)
# not sure how to unlock if you set a non-zero lock number
# and know what it is
def Command_MCALock (lock_number) :
    if not isinstance (lock_number, int) :
        raise TypeError ('LockNumberNotInt')
    if lock_number < 0 :
        raise ValueError ('LockNumberLow')
    if lock_number >= 2**16 :
        raise ValueError ('LockNumberHigh')
    command_byte = 117
    # note that the lower and upper byte positions are actually not defined
    # in the protocol manual
    byte1 = lock_number % 256 # lower byte
    byte2 = lock_number // 256 # upper byte
    byte3 = 1 # doesn't matter, but can't be zero
    command = bytearray ([command_byte, byte1, byte2, byte3])
    return addCheckSum (command)
    
def Command_DeleteDataAndTime (delete_data=True, delete_time=True) :
    command_byte = 5
    byte1 = 1 if delete_data else 0
    byte2 = 1 if delete_time else 0
    byte3 = 1
    command = bytearray ([command_byte, byte1, byte2, byte3])
    return addCheckSum (command)

def Command_PresetTime (preset) :
    if not isinstance (preset, int) :
        raise TypeError ('PresetNotInt')
    if preset < 0 :
        raise ValueError ('PresetLow')
    if preset >= 2**24 :
        raise ValueError ('PresetHigh')
    command_byte = 2
    byte3 = preset // 2**16
    remainder = preset % 2**16
    byte2 = remainder // 256
    byte1 = remainder % 256
    command = bytearray ([command_byte, byte1, byte2, byte3])
    return addCheckSum (command)
    
class MCA8000A :
    def __init__ (self, device_path, baudrate=4800, isMacFTDI=False) :
        self.device_path = device_path
        self.baudrate = baudrate # this doesn't do anything right now
        self.isMacFTDI = isMacFTDI
        # should probably get rid of it
        self.serial_connection = serial.Serial \
            (self.device_path, baudrate=4800, parity='E',
             timeout=0.2, write_timeout=0.2)
        self.oldcts = self.serial_connection.cts
        self.olddsr = self.serial_connection.dsr
        self.debug = False
        self.is_USB_MCA = False # default
        # status variables
        self.SerialNumber = 0 # dummy
        self.Group = 0
        self.LastDataCheckSum = 0 # dummy
        self.PresetTime = 0.0
        self.RealTime = 0.0
        self.LiveTime = 0.0
        self.BatteryStatus = 0
        self.Threshold = 0
        # status from flags
        self.flags = 0 # store flags byte as well
        self.ADCResolution = 2**14
        self.isLive = False
        self.isRunning = False
        self.isProtected = False
        self.isNiCad = False
        self.isBackupBatteryBad = False
        # data
        self.ChannelData = None
        self.ChannelDataFloat = None
        
    def ResetRTS (self) :
        self.serial_connection.rts = False

    def SetRTS (self) :
        self.serial_connection.rts = True

    def GetRTS (self) :
        return self.serial_connection.rts


    def ResetDTR (self) :
        self.serial_connection.dtr = False

    def SetDTR (self) :
        self.serial_connection.dtr = True

    def ToggleDTR (self) :
        self.serial_connection.dtr = ~self.serial_connection.dtr


    def PurgeRX (self) :
        self.serial_connection.reset_input_buffer ()

    def PurgeTX (self):
        self.serial_connection.reset_output_buffer ()
        
    def RememberCTS (self) :
        self.oldcts = self.serial_connection.cts

    def IsCTSFlipped (self) :
        return self.oldcts != self.serial_connection.cts

    def RememberDSR (self) :
        self.olddsr = self.serial_connection.dsr

    def IsDSRFlipped (self) :
        return self.olddsr != self.serial_connection.dsr

    def PrintStatus (self) :
        print ("Serial Number:\t {}".format (self.SerialNumber))
        print ("Group:\t {}".format (self.Group))
        print ("Preset Time:\t {}".format (self.PresetTime))
        print ("Real Time:\t {}".format (self.RealTime))
        print ("Live Time:\t {}".format (self.LiveTime))
        print ("BatteryStatus:\t {}".format (self.BatteryStatus))
        print ("Threshold:\t {}".format (self.Threshold))
        print ("ADC Resolution:\t {}".format (self.ADCResolution))
        if self.isLive :
            print ("Using live timer")
        else :
            print ("Using real timer")
        if self.isRunning :
            print ("Acquiring data")
        else :
            print ("Not acquiring data")
        MCAsecurity = "Protected" if self.isProtected else "Public"
        print ("MCA security:\t {}".format (MCAsecurity))
        BatteryType = 'NiCad' if self.isNiCad else 'Alkaline'
        print ("Battery type:\t {}".format (BatteryType))
        BackupBatteryStatus = 'bad' if self.isBackupBatteryBad else 'good'
        print ("Backup battery is {}".format (BackupBatteryStatus))
        return
        
    def PowerOn (self, freq=2000, duration=0.1, power_on_time=4.0) : # Hz, s, s
        # spec is 1-200 kHz for > 50 ms 
        # the 4 s is from the code, probably could shorten
        delay = 0.5 / freq # delay for half a cycle
        ncycles = int (duration * freq)
        # close and open port in case something is messed up
        self.serial_connection.close ()
        self.serial_connection.open ()
        self.SetRTS ()
        for i in range (ncycles) :
            self.SetDTR ()
            wait (delay)
            self.ResetDTR ()
            wait (delay)
        # give it plenty of time to flip bits
        wait (power_on_time - duration)
        # verify correct USB behavior; old-style protocol not supported
        is_USB_MCA_CTS = (self.serial_connection.cts != self.oldcts)
        is_USB_MCA_DSR = (self.serial_connection.dsr == self.olddsr)


        print(self.serial_connection.cts, self.oldcts, is_USB_MCA_CTS)
        print(self.serial_connection.dsr, self.olddsr, is_USB_MCA_DSR)

        if (is_USB_MCA_CTS == is_USB_MCA_DSR) :
            self.is_USB_MCA = is_USB_MCA_CTS
            if self.debug :
                print ("USBMCA == {}".format (self.is_USB_MCA))
            if not self.is_USB_MCA :
                print ("This is not a USB MCA. It is not supported.")
        else :
            self.is_USB_MCA = False
            print ("Error identifying MCA type.")
            print ("I think this is old MCA.")
            
        self.ResetRTS ()
        self.RememberCTS ()
        # close port? doesn't seem necessary
        return

    def WaitForCTSFlip (self, delay=0.2) :
        timeout = timeit.default_timer () + delay
        while (True) :
            if self.IsCTSFlipped () :
                self.RememberCTS ()
                return 0 # success
            if timeit.default_timer () > timeout :
                if self.debug : print ("WaitForCTSFlip: CTS did not flip")
                return 1 # failure
        return 2 # should not get here

    def WaitForDSRFlip (self, delay=0.2) :
        timeout = timeit.default_timer () + delay
        while (True) :
            if self.IsDSRFlipped () :
                self.RememberDSR ()
                return 0 # success
            if timeit.default_timer () > timeout :
                if self.debug : print ("WaitForDSRFlip: DSR did not flip")
                return 1 # failure
        return 2 # should not get here


    def WaitToSendData (self, delay=0.2) :
        timeout = timeit.default_timer () + delay
        while (True) :
            if self.serial_connection.out_waiting == 0 :
                return 0 # success
            if timeit.default_timer () > timeout :
                if self.debug : print ("Writing timed out")
                return 1 # failure
        return 2 # should not get here

    # this function only does the actual write command on the serial port
    # the behavior depends on self.isMacFTDI
    # if true, then it writes individual bytes
    # and pauses to let the FTDI chip finish sending each byte
    # this is because of an apparent bug in the MacOS FTDI driver
    def SendCommandBytes (self, commandbytes) :
        bytes_send = 0
        if self.isMacFTDI :
            single_byte_delay = 10.0 / self.baudrate # time to send 10 bits
            for i in range (len (commandbytes)) :
                self.serial_connection.write ((bytes([commandbytes[i]])))
                # the syntax of the preceding line is needed to
                # make a bytes object of length one
                # a single element of a bytearray i.e. commandbytes[i] is an int
                # so we make that into a list with length one
                # and cast it as bytes
                stat = self.WaitToSendData ()
                if stat : return stat
                wait (single_byte_delay)
            return 0
        else :
            for i in range (len (commandbytes)) :
                if self.WaitForDSRFlip () :
                    if self.debug : print ("SendCommandBytes: Wait DSR flip failed")
                    continue
                self.serial_connection.write (bytes([commandbytes[i]]))
                bytes_send += 1
                stat = self.WaitToSendData ()
                if stat : return stat
            if self.debug : print ("SendCommandBytes: %s bytes send." % bytes_send)
            return 0

    def SendCommand (self, command, n_retries=10) :
#        for i in range (n_retries) :
#            if self.debug : print ("Retry number {}".format (i))

            # get ready
        #self.PurgeTX ()
        #self.RememberCTS ()
        #self.RememberDSR ()

#        self.ResetDTR()
            # set RTS and check for CTS flip
#        wait(0.2)
#        self.SetRTS () # its Magic !
#        wait(0.2)
        
        self.ResetRTS ()
        self.SetDTR ()

        for i in range (n_retries) :
            if self.debug : print ("SendCommand: Retry number {}".format (i))

            self.SetRTS () # Prepare PMCA to receive command
#            self.SetDTR ()

            if self.is_USB_MCA:
                if self.debug : print ("SendCommand: AHTUNG !!!")
                if self.WaitForCTSFlip () :
                    if self.debug : print ("SendCommand: First CTS flip failed")
                    #self.ResetRTS ()
                    continue # retry
            # make sure the buffer for receiving MCA data is cleared
                self.PurgeRX ()

            # check for 2nd CTS flip
                if self.WaitForCTSFlip () :
                    if self.debug : print ("SendCommand: Second CTS flip failed")
                    #self.ResetRTS ()
                    #continue # retry
            else:
                #for i in range (len (commandbytes)) :
                if self.WaitForDSRFlip () :
                    if self.debug : print ("SendCommand: First DSR flip failed")
                    self.ResetRTS ()
 #                   self.ResetDTR ()
                    if self.is_USB_MCA==False:
                        wait(0.02)
                    continue # retry

            # send data
            #self.serial_connection.write (command)
                self.SendCommandBytes (command)
                if self.WaitForDSRFlip () :
                    if self.debug : print ("SendCommand: Second DSR flip failed")
                    
            self.ResetRTS () # Tell PMCA to exit the receive state
            
            
            if self.is_USB_MCA==False:
                wait(0.02)
                            
#            if self.WaitToSendData () :
#                if self.debug : print ("Writing data failed")
#                self.ResetRTS ()
#                self.ResetDTR ()
#                continue # retry
#            self.PurgeRX () # apparently sometimes an extra byte shows up early?
            # end transmission
#            self.ResetRTS ()
           
            return 0 # sending command succeeded

        print ("SendCommand: Sending command failed")
        return 1 # failure

    #def GetStatus (self) :
    #    self.serial_connection.rts = True
    #    if self.WaitForCTSFlip () :
    #        if self.debug : print ("GetStatus: CTS flip failed")
    #        return 1 # failure
    #    self.serial_connection.rts = False
    #    # should break the below to a separate function
    #    timeout = timeit.default_timer () + delay
    #    outdata = bytearray ()
    #    while (True) :
    #        if (self.serial_connection.in_waiting > 0) :
    #            timeout = timeit.default_timer () + delay # reset
    #            outdata.append (self.serial_connection.read (1))
    #        if timeit.default_timer () > timeout :
    #            print ("GetStatus: read timeout")
    #            return 1 # failure
    #        if len (outdata) == 20 :
    #            break # done getting data
    #    # just print bytes for now
    #    for i in range (20) :
    #        print (outdata[i])
    #    return 0


    def SetBaudRate (self, baudrate) :
        if 115200 % baudrate > 0 :
            print ("SetBaudRate: Baudrate must be integer divisor of 115200")
            return 1 # failure
        divisor = 115200 // baudrate
        comm = Command_SetBaudRate (divisor)
        
        self.RememberDSR()
        # clear
#        self.ResetDTR ()
#        self.ResetRTS ()
#        wait (0.1)
        # send command
#        self.SetRTS ()
#        self.SetDTR ()
        stat = self.SendCommand (comm)
#        self.ResetDTR ()
        if stat :
            print ("SetBaudRate: couldn't send command")
            # SHOULDN'T IT RESET RTS?
            return 1 # failure    
        # set baudrate on comm port, clear
        self.serial_connection.baudrate = baudrate
        #self.serial_connection.rts = False # should already be zero
#        self.ResetRTS ()
#        self.SetDTR ()
        wait (0.2)
      
#        self.ReceiveStatusFromPrompt ()
        self.PurgeRX () # throw out whatever's in there

        # SHOULDN'T IT RESET RTS?
        # get status to confirm it's OK
        #self.GetStatus () # FIX ME
        return 0
    

    def PromptForStatus (self) :

        self.ResetRTS () # First clear RTS to make sure that PMCA is in the send state
        wait (0.0002)
        # could add a line to ensure oldcts is set
        # could add a check for serial connection status
        
        self.SetRTS ()
        
        if self.is_USB_MCA:
            print("AHTUNG!!!")
            stat = self.WaitForCTSFlip ()
            self.PurgeRX ()        
        else:
            stat = self.WaitForDSRFlip ()
        self.ResetRTS ()
        wait (0.0002)
        print("PromptForStatus: rts %s" % self.GetRTS())
        
        
        return stat

    # can this every be called without serial number?
    def ReceiveStatusFromPrompt (self) :
        stat = self.PromptForStatus ()
        if not stat :
            stat = self.ReceiveStatusWithRetry ()
        return stat

    def ReceiveStatusWithRetry (self, nretries=10) :
        for i in range (nretries) :
            stat = self.ReceiveStatus (hasSerialNumber=True)
            if not stat : # success
                return stat
            stat = self.PromptForStatus ()
            if stat : # failure
                break
        return stat

    def ReceiveStatus (self, hasSerialNumber=False) :
        print ("ReceiveStatus: receive status data...")
        stat, StatusData = self.ReceiveData (20) # 20 ?
        if stat:
            print ("ReceiveStatus: error getting status bytes")
            return 1
        #timeout = timeit.default_timer () + delay
        #outdata = bytearray ()
        #while (True) :
        #    if (self.serial_connection.in_waiting > 0) :
        #        timeout = timeit.default_timer () + delay # reset
        #        outdata.append (self.serial_connection.read (1)[0])
        #    if timeit.default_timer () > timeout :
        #        print ("ReceiveStatus: read timeout")
        #        return 1 # failure
        #    if len (outdata) == 20 :
        #        break # done getting data
        stat = self.UpdateStatusFromData (StatusData, hasSerialNumber)
        if stat :
            print ("ReceiveStatus: failed in UpdateStatusFromData")
            return 1
        return 0 # success

    def ReceiveStatusCheckSum (self) :
        stat, StatusData = self.ReceiveData (20) # 20 ?
        if stat:
            return stat, NULL
        return stat, int.from_bytes (StatusData[:4], "big")

    def UpdateStatusFromData (self, data, hasSerialNumber=False) :
    
#        cs1 = int.from_bytes (data[0:4], "big")
#        cs2 = cs1 & 0xff
        checksum = data[-1]
        datasum = sum (data[:-1]) % 256
#        datasum1 = sum (data[0:18]) & 0xff

#        print(cs1,cs2,checksum,datasum,datasum1)
#        print(data[16],data[17])
#        print("thrs= %s" % int.from_bytes (data[15:17], "big"))
        if checksum != datasum :
            print ("UpdateStatusFromData: checksum error")
            if self.debug :
                for i in range (20) : # 20 ?
                    print (data[i])
            return 1 # failure
        #for i in range (20) : # 20 ?
        #    print (data[i])

        #should do something with checksum if hasSerialNumber=False
        if hasSerialNumber :
            self.SerialNumber = int.from_bytes (data[0:2], "big")
            # I think group number is the next two bytes
            # but I did not check
        else :
            self.LastDataCheckSum = int.from_bytes (data[0:4], "big")
        self.PresetTime = int.from_bytes (data[4:7], "big")
        self.BatteryStatus = data[7] # leave as int
        self.RealTime = int.from_bytes (data[8:11], "big")
        RealTime75 = data[11]
        self.RealTime += (1.0 - RealTime75 / 75)
        self.LiveTime = int.from_bytes (data[12:15], "big")
        LiveTime75 = data[15]
        self.LiveTime += (1.0 - LiveTime75 / 75)
        self.Threshold = int.from_bytes (data[16:18], "big")
        self.flags = data[18]
        # parse flags
        ADCRes_bits = self.flags & 0b111 # resolution info is in bits 0-2
        self.ADCResolution = 2**(14-ADCRes_bits)
        self.isLive = bool ((self.flags >> 3) & 1)
        # live/real timer flag is bit 3
        self.isRunning = bool ((self.flags >> 4 ) & 1)
        # start/stop is bit 4
        self.isProtected = bool ((self.flags >> 5) & 1)
        # protected/public is bit 5
        self.isNiCad = bool ((self.flags >> 6) & 1)
        # NiCad/Alkaline is bit 6
        self.isBackupBatteryBad = bool ((self.flags >> 7) & 1)
        # backup battery bad/OK is bit 7
        return 0

    # returns status and data
    # if status is bad don't use data
    def ReceiveData (self, nbytes, delay=0.2) :

        if self.is_USB_MCA==False:
            self.PurgeRX ()   

        self.ResetRTS()

        self.ResetDTR() # Magic ???
    
        if self.is_USB_MCA:
            delay = 0.75 # time out in 0.75 second
        else:
            delay = 0.5
                       
        timeout = timeit.default_timer () + delay
        outdata = bytearray ()
        
        
        divisor = 115200 // 4800
        byteTime = divisor * (15000000.0 / 115200);
        
        #print("divisor, byteTime %s %s" % (divisor, byteTime))
        

        while (True) :
            available = self.serial_connection.in_waiting
            
#            if (available) :
#                outdata += self.serial_connection.read (1) #nbytes_to_get)
#                print ("ReceiveData: data %s %s" % (outdata, len (outdata)))  
                                                     
            if (available) :
                if self.is_USB_MCA==False:
                    print ("ReceiveData: ToggleDTR")
                    for i in range(0,nbytes):
                        self.ToggleDTR()
                        wait(0.0003)
                    break

        
        while (True) :
            available = self.serial_connection.in_waiting
#            print("available %s" % available)
            if (available) :
                #print ("ReceiveData: reading...")                        
                timeout = timeit.default_timer () + delay # reset timer
                # read whatever you can get, but don't go over nbytes
                nbytes_to_get = min (available, nbytes - len (outdata))
                outdata += self.serial_connection.read (1) #nbytes_to_get)
                #print ("ReceiveData: data %s %s" % (outdata, len (outdata)))                                       
            if timeit.default_timer () > timeout :
                #print ("ReceiveData: read timeout")
                return 1, None  # failure
            if len (outdata) >= nbytes : # done getting data
                if len (outdata) > nbytes :
                    return 1, outdata # got more than we expected
                else :
                    #print ("ReceiveData: success")
                    return 0, outdata
        return 1, None

    def ReceiveChannelData (self) :
        # this only works for resolution 1024 or below
        # I see unexpected behavior for the get data commands
        # when it's called with parameters other than 0,1024
        # and even for that parameter, I see weird data for
        # high channel numbers > 1000
        words_requested = min (self.ADCResolution, 1024)
        start_channel = 0
        # first get the lower words
        comm = Command_SendData (start_channel, words_requested)

        print ("ReceiveChannelData: first get the lower words")

        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData1: error sending command")
            return stat
        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData1: failed getting status")
        stat, lowerdata = self.ReceiveData (words_requested*2)
        if stat :
            print ("ReceiveChannelData1: error receiving data")
            return stat
        lowerdatachecksum = sum (lowerdata) % (2**16) # Amptek's prescription

        self.SetRTS () # Magic ???
        print ("ReceiveChannelData: now get the upper words")
        
        # now get the upper words
        comm = Command_SendData (start_channel, words_requested, upper=True)
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData2: error sending command")
            return stat
        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData2: failed getting status")
        # ReceiveStatus updated the checksum, now check it
        if lowerdatachecksum != self.LastDataCheckSum :
            print ("ReceiveChannelData2: lower word checksum failed")
            return 1
        # now get the upper word data
        stat, upperdata = self.ReceiveData (words_requested*2)
        if stat :
            print ("ReceiveChannelData2: error receiving data")
            return stat
        upperdatachecksum = sum (upperdata)  % (2**16)
        # ask for 64 words of data to prompt a status with checksum
        dummy_words_requested = 64
        comm = Command_SendData (0,dummy_words_requested)
        # tried asking for one but for some reason that seemed to be a problem
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData3: error sending command")
            return stat
        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData: failed getting status")
        # ReceiveStatus updated the checksum, now check it
        if upperdatachecksum != self.LastDataCheckSum :
            print ("ReceiveChannelData3: lower word checksum failed")
            return 1
        # get the words; purging seems to not work reliably, so just read all
        stat, dummydata = self.ReceiveData (dummy_words_requested*2)
        if stat :
            print ("ReceiveChannelData3: error receiving data")
            return stat
        # throw away the dummy data
        #self.PurgeRX () # throw out the remaining byte

        lower = np.frombuffer (lowerdata, dtype=np.int16)
        upper = np.frombuffer (upperdata, dtype=np.int16)
        self.ChannelData = lower + upper * 2**16
        return 0


    def ReceiveChannelDataOld (self) :
        # this only works for resolution 1024 or below
        # I see unexpected behavior for the get data commands
        # when it's called with parameters other than 0,1024
        # and even for that parameter, I see weird data for
        # high channel numbers > 1000
#        words_requested = min (self.ADCResolution, 1024)
        words_requested = 1024*2
        start_channel = 0
        # first get the lower words
        comm = Command_SendDataOld (start_channel, group=True)

        print ("ReceiveChannelData: first get the lower words")
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData1: error sending command")
            return stat
        wait(1)
        stat = self.PromptForStatus ()
        stat = self.ReceiveStatusWithRetry ()
#        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData1: failed getting status")
        #stat = self.PromptForStatus ()
        stat, lowerdata = self.ReceiveData (words_requested)
        if stat :
            print ("ReceiveChannelData1: error receiving data")
            return stat
        lowerdatachecksum = sum (lowerdata) % (2**16) # Amptek's prescription

        print(lowerdata)

        self.SetRTS()

        comm = Command_SendDataOld (start_channel, group=True)
        print ("ReceiveChannelData: try to get final status")
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData1: error sending command")
            return stat
        stat = self.PromptForStatus ()
        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData1: failed getting final status")


        self.SetRTS()
        
        # second get the upper words
        comm = Command_SendDataOld (start_channel, group=True, upper=True)

        print ("ReceiveChannelData: second get the upper words")
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData2: error sending command")
            return stat
        wait(1)
        stat = self.PromptForStatus ()
        stat = self.ReceiveStatusWithRetry ()
#        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData2: failed getting status")
        #stat = self.PromptForStatus ()
        stat, upperdata = self.ReceiveData (words_requested)
        if stat :
            print ("ReceiveChannelData2: error receiving data")
            return stat
        upperdatachecksum = sum (lowerdata) % (2**16) # Amptek's prescription

        print(upperdata)

        self.SetRTS()

        comm = Command_SendDataOld (start_channel, group=True)
        print ("ReceiveChannelData2: try to get final status")
        stat = self.SendCommand (comm)
        if stat :
            print ("ReceiveChannelData2: error sending command")
            return stat
        stat = self.PromptForStatus ()
        stat = self.ReceiveStatus () # no S/N
        if stat :
            print ("ReceiveChannelData2: failed getting final status")

        lower = np.frombuffer (lowerdata, dtype=np.int16)
        upper = np.frombuffer (upperdata, dtype=np.int16)
        self.ChannelData = lower + upper * 2**16
        self.ChannelDataFloat = (lower + upper * 2**16)/4294967295


        return 0



        
    def SetThreshold (self, threshold) :
        # user existing flags variable
        command = Command_Control (self.flags, threshold)         
        stat = self.SendCommand (command)
        if stat :
            print ("SetThreshold: error sending command")
            return stat
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("SetThreshold: error updating status")
            return stat
        return 0

    def SetLock (self, lock_number) :
        command = Command_MCALock (lock_number)
        stat = self.SendCommand (command)
        if stat :
            print ("SetLock: error sending command")
            return stat
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("SetLock: error updating status")
            return stat
        return 0

    def SetLockToZero (self) :
        command = Command_MCALock (0)
        stat = self.SendCommand (command)
        if stat :
            print ("SetLock: error sending command")
            return stat
        wait (4.0)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("SetLock: error updating status")
            return stat
        return 0

    # I think you can't just set public.
    # Probably you have to unlock with a code.
    #def SetPublic (self) :
    #    flags = self.flags & 0b11011111 # set protected bit to zero
    #    command = Command_Control (flags, self.Threshold)
    #    stat = self.SendCommand (command)
    #    if stat :
    #        print ("SetPublic: error sending command")
    #        return stat
    #    wait (0.5)
    #    stat = self.ReceiveStatusFromPrompt ()
    #    if stat :
    #        print ("SetPublic: error updating status")
    #        return stat
    #    return 0
    
    def SetADCResolution (self, channels) :
        # rounds channels up to nearest power of two
        # here is the code that sets resolution from bits:
        # self.ADCResolution = 2**(14-ADCRes_bits)
        if not isinstance (channels, int) :
            raise TypeError ('ChannelsNotInt')
        if channels < 128 :
            raise ValueError ('ChannelsLow')
        if channels > 2**14 :
            raise ValueError ('ChannelsHigh')
        # there's probably a more elegant way to do all this
        # set a flag to round up if more than one bit is 1
        roundup = True if bin (channels).count ("1") > 1 else False
        ADCRes_bits = 0
        for i in range (14) :
            temp = channels << i
            if temp & 2**14 :
                ADCRes_bits = i
                break
        if roundup : ADCRes_bits -= 1
        print (ADCRes_bits)
        newflags = (0b11111000 & self.flags) + (0b00000111 & ADCRes_bits)
        print (newflags)
        command = Command_Control (newflags, self.Threshold)         
        stat = self.SendCommand (command)
        if stat :
            print ("SetADCResolution: error sending command")
            return stat
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("SetADCResolution: error updating status")
            return stat
        return 0






    # delay sets time between sending start and asking for status
    def StartAcquisition (self, delay=1.0) :
        newflags = self.flags | 0b10000 # set bit 4 to one
        command = Command_Control (newflags, self.Threshold)         
        stat = self.SendCommand (command)
        if stat :
            print ("StartAcquisition: error sending command")
            return stat
        print ("StartAcquisition: command already send")
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("StartAcquisition: error updating status")
            return stat
        return 0

    # delay sets time between sending stop and asking for status
    def StopAcquisition (self, delay=0.2) :
        newflags = self.flags & 0b11101111 # set bit 4 to zero
        command = Command_Control (newflags, self.Threshold)         
        stat = self.SendCommand (command)
        if stat :
            print ("StopAcquisition: error sending command")
            return stat
        print ("StopAcquisition: command already send")
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("StopAcquisition: error updating status")
            return stat
        return 0

    def DeleteDataAndTime (self, delay=0.2) :
        command = Command_DeleteDataAndTime () # default is both
        stat = self.SendCommand (command)
        if stat :
            print ("DeleteDataAndTime: error sending command")
            return stat
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("DeleteDataAndTime: error updating status")
            return stat
        return 0

    def DeleteData (self, delay=0.2) :
        command = Command_DeleteDataAndTime (delete_time=False)
        stat = self.SendCommand (command)
        if stat :
            print ("DeleteData: error sending command")
            return stat
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("DeleteData: error updating status")
            return stat
        return 0

    def DeleteTime (self, delay=0.2) :
        command = Command_DeleteDataAndTime (delete_data=False)
        stat = self.SendCommand (command)
        if stat :
            print ("DeleteTime: error sending command")
            return stat
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("DeleteTime: error updating status")
            return stat
        return 0

    def SetPresetTime (self, time, delay=0.2) :
        command = Command_PresetTime (time)
        stat = self.SendCommand (command)
        if stat :
            print ("PresetTime: error sending command")
            return stat
        wait (delay)
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("PresetTime: error updating status")
            return stat
        return 0

    def Initialize (self, baudrate=115200) :
    
#        self.ResetRTS () # Magic ???

#        self.SetDTR() # DTR must be high for autoconnect

#        comm = Command_SendData (0, 1024, upper=True)
#        print("Initialize: Try to send %s" % comm)
#        self.SendCommand(comm)

#        self.ResetDTR()
    
        print(self.serial_connection.is_open)
        
        print("Initialize: Try to set threshold1")
        self.SetThreshold(40)

        wait(0.2)
#        return 0
    
#        stat = self.ReceiveStatusFromPrompt ()
#        if stat :
#            print ("Initialize: error getting status")
#            return stat

        self.SetRTS () # Magic ???
        #self.SetDTR() # DTR must be high for autoconnect

#        print ("Setting baud rate")
#        stat = self.SetBaudRate (115200)
       
        wait(0.2)

#        self.SetDTR() # Magic ???
#        self.SetRTS () # Magic ???
        print("Initialize: Try to set threshold2")
        self.SetThreshold(50)

        self.SetRTS () # Magic ???
        wait(0.2)
        print("Initialize: Try to set threshold3")
        self.SetThreshold(1000)


        self.SetRTS () # Magic ???
        print("Initialize: Try to START...")
        self.StartAcquisition()

        wait(3)
        
        
        self.SetRTS () # Magic ???
        wait(0.2)
        print("Initialize: Try to RECEIVE...")
        self.ReceiveChannelDataOld()

        self.SetRTS () # Magic ???

        print("Initialize: Try to STOP...")
        self.StopAcquisition()


        
        print(self.ChannelData)
        
        
        file = open('test.dat','w')
        
        for i in range(0,len(self.ChannelDataFloat)):
            file.write("%s\n" % self.ChannelDataFloat[i])
        file.close()
            
#        print(self.ChannelDataFloat)


        return 0

        if stat :
            print ("Initialize: error setting baud rate")
            return stat
        stat = self.ReceiveStatusFromPrompt ()
        if stat :
            print ("Initialize: error getting status")
            return stat
        return 0
    
# Tests #####################################################################
def test_mca():
  mca = MCA8000A("/dev/ttyUSB1")
  mca.debug = True
  
  mca.PowerOn()
  mca.Initialize()

  mca.PrintStatus()    
#  mca.PromptForStatus()
#  print("ReceiveStatusFromPrompt= %s" % mca.ReceiveStatusFromPrompt())
  
#  mca.SetBaudRate(115200)
  
#  mca.StartAcquisition()
#  mca.ReceiveChannelData()
#  mca.StopAcquisition()  
    
    # to be implemented
    
    # set group

    # set start time
    # set start date
    # get start time
    # get start date

    # I don't think these are needed if you don't care about recording
    # the external time of the experiment


    # need to test these, but they almost certainly work
    # clear data

    # clear data and time


