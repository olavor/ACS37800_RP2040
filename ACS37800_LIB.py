from micropython import const
import ustruct,time, utime
from machine import Pin, I2C
i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000) 
#testado dia 23/10/2025 sucesso
ACS37800_DEFAULT_I2C_ADDRESS = const(0x60)
ACS37800_CUSTOMER_ACCESS_CODE = const(0x4F70656E)
# Resistência de sense padrão para medição de tensão (Ohms)
ACS37800_DEFAULT_SENSE_RES = const(1982.0)
# Resistência padrão do divisor de tensão para medição de tensão (Ohms)
ACS37800_DEFAULT_DIVIDER_RES = const(2000000.0)
# ACS37800KMACTR-030B3-I2C é uma peça de 30.0 Amp 
ACS37800_DEFAULT_CURRENT_RANGE = const(30.0)
# Códigos de erro (substituindo o enum do C)
ACS37800_SUCCESS = const(0) #False
ACS37800_ERR_I2C_ERROR = const(1) 
ACS37800_ERR_REGISTER_READ_MODIFY_WRITE_FAILURE = const(2)
# EEPROM Registers
ACS37800_REGISTER_EEPROM_0B = const(0x0B)
ACS37800_REGISTER_EEPROM_0C = const(0x0C)
ACS37800_REGISTER_EEPROM_0D = const(0x0D)
ACS37800_REGISTER_EEPROM_0E = const(0x0E)
ACS37800_REGISTER_EEPROM_0F = const(0x0F)
# Ao ligar, todos os registradores de sombra são carregados da EEPROM, incluindo todos os parâmetros de configuração.
# Os registradores de sombra podem ser gravados para alterar o comportamento do dispositivo sem a necessidade de
# realizar uma gravação na EEPROM. Quaisquer alterações feitas na memória de sombra são voláteis e não persistem após um evento de reinicialização. 
ACS37800_REGISTER_SHADOW_1B = const(0x1B)
ACS37800_REGISTER_SHADOW_1C = const(0x1C)
ACS37800_REGISTER_SHADOW_1D = const(0x1D)
ACS37800_REGISTER_SHADOW_1E = const(0x1E)
ACS37800_REGISTER_SHADOW_1F = const(0x1F)
# Volatile Registers
ACS37800_REGISTER_VOLATILE_20 = const(0x20)
ACS37800_REGISTER_VOLATILE_21 = const(0x21)
ACS37800_REGISTER_VOLATILE_22 = const(0x22)
ACS37800_REGISTER_VOLATILE_25 = const(0x25)
ACS37800_REGISTER_VOLATILE_26 = const(0x26)
ACS37800_REGISTER_VOLATILE_27 = const(0x27)
ACS37800_REGISTER_VOLATILE_28 = const(0x28)
ACS37800_REGISTER_VOLATILE_29 = const(0x29)
ACS37800_REGISTER_VOLATILE_2A = const(0x2A)
ACS37800_REGISTER_VOLATILE_2C = const(0x2C)
ACS37800_REGISTER_VOLATILE_2D = const(0x2D)
ACS37800_REGISTER_VOLATILE_2F = const(0x2F)
ACS37800_REGISTER_VOLATILE_30 = const(0x30)
# Enumeradores (valores inteiros constantes)
ACS37800_CRS_SNS_1X          = 0
ACS37800_CRS_SNS_2X          = 1
ACS37800_CRS_SNS_3X          = 2
ACS37800_CRS_SNS_3POINT5X    = 3
ACS37800_CRS_SNS_4X          = 4
ACS37800_CRS_SNS_4POINT5X    = 5  # valor padrão
ACS37800_CRS_SNS_5POINT5X    = 6
ACS37800_CRS_SNS_8X          = 7

# Tabela de ganhos (usa tupla: imutável e mais leve que lista no MicroPython)
ACS37800_CRS_SNS_GAINS = (1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.5, 8.0)
# Fault Delay (FLTDLY)
ACS37800_FLTDLY_0000   = 0
ACS37800_FLTDLY_0475   = 2  # 4.75 µs
ACS37800_FLTDLY_0925   = 3  # 9.25 µs
ACS37800_FLTDLY_1375   = 4
ACS37800_FLTDLY_1850   = 5
ACS37800_FLTDLY_2325   = 6
ACS37800_FLTDLY_2775   = 7  # 27.75 µs

# DIO0 Function
ACS37800_DIO0_FUNC_ZERO_CROSSING = 0
ACS37800_DIO0_FUNC_OVERVOLTAGE   = 1
ACS37800_DIO0_FUNC_UNDERVOLTAGE  = 2
ACS37800_DIO0_FUNC_OV_OR_UV      = 3

# DIO1 Function
ACS37800_DIO1_FUNC_OVERCURRENT           = 0
ACS37800_DIO1_FUNC_UNDERVOLTAGE          = 1
ACS37800_DIO1_FUNC_OVERVOLTAGE           = 2
ACS37800_DIO1_FUNC_OV_OR_UV_OR_OCF_LAT   = 3

# EEPROM ECC Errors
ACS37800_EEPROM_ECC_NO_ERROR          = 0
ACS37800_EEPROM_ECC_ERROR_CORRECTED   = 1
ACS37800_EEPROM_ECC_ERROR_UNCORRECTABLE = 2
ACS37800_EEPROM_ECC_NO_MEANING        = 3

def read_register(register, device_address):
    try: 
        x = bytes([register])
        i2c.writeto(device_address, x)
        data1 = bytearray(4)# Write register address
        i2c.readfrom_into(device_address, data1)
        print("ponto1")#data1 é Little Endian LSB
        if len(data1) != 4:
            return None, False      # Combine bytes (little endian)
            print("opa erro!")
        else:#Big Endian
            read_data = data1[0] | (data1[1] << 8) | (data1[2] << 16) | (data1[3] << 24)
            print("tudo certo!")
            return read_data, True  # Success
    except:
        return 0, False
    
def write_register(address, register, data):
    data2 = bytearray((data >> (8*i)) & 0xFF for i in range(4))
    try:# Prepare data: register address + 4 bytes (little endian)
        i2c.writeto_mem(address, register, data2)# Write data
        print("ponto22")
        return True  # Success
    except:
        return False  # Error
        print("ponto_errado")
########################&&&&&&&&&&&&&&&&
def setNumberOfSamples(numberOfSamples, _eeprom):
    success = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_VOLATILE_2F, ACS37800_CUSTOMER_ACCESS_CODE)
    time.sleep_ms(100)
    if success == True:
        print("setNumberOfSamples: writeRegister (2F) returned:", success)
    
    shadow_value, error = read_register(ACS37800_REGISTER_SHADOW_1F,ACS37800_DEFAULT_I2C_ADDRESS)
    new_shadow_value = shadow_value & 0x3FF
    if error != ACS37800_SUCCESS:
        print("setNumberOfSamples: read_register (1F) returned:", new_shadow_value)
    
    samples = numberOfSamples & 0x3FF
    success = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_SHADOW_1F, samples)
    time.sleep_ms(100)
    if success == True:
        print("setNumberOfSamples: write_register (1F) returned:", success)
       
    if _eeprom:
        eeprom_value, error = read_register(ACS37800_REGISTER_EEPROM_0F, ACS37800_DEFAULT_I2C_ADDRESS)
        time.sleep_ms(100)
        new_eeprom_value =  eeprom_value & 0x3FF
        if error != ACS37800_SUCCESS:
            print("setNumberOfSamples: readregister (0F) returned:", new_eeprom_value)
           
        data4 = numberOfSamples & 0x3FF
        success = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_EEPROM_0F, data4)
        time.sleep_ms(100)
        if success == True:
                print("setNumberOfSamples: writeRegister (0F) returned:", error)
    
    error = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_VOLATILE_2F, 0)
    time.sleep_ms(100)
    if error != ACS37800_SUCCESS:
        print("setNumberOfSamples: writeregister (2F) returned:", error)
    time.sleep_ms(100)
    return error
#===================================================================
def set_bypass_n_enable(bypass, save_to_eeprom):
    # 1. Unlock
    ok = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_VOLATILE_2F, ACS37800_CUSTOMER_ACCESS_CODE)
    time.sleep_ms(100)
    print(ok)
    # 2. Read current config
    shadow_value, success = read_register(ACS37800_REGISTER_SHADOW_1F,ACS37800_DEFAULT_I2C_ADDRESS)
    time.sleep_ms(100)
    print(success)
    # 3. Modify only the bypass_n_en bit (bit 24 na estrutura)
    if bypass: #Big Endian
        new_value = shadow_value | (1 << 24)    # Seta bit 24 para 1
    else: #Big Endian
        new_value = shadow_value & ~(1 << 24)   # Seta bit 24 para 0
    
    # 4. Write back
    feedback= write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_SHADOW_1F, new_value)
    time.sleep_ms(100)
    print(feedback)
    # 5. Optional EEPROM save
    print("save_to_eeprom: ", save_to_eeprom)
    if save_to_eeprom:
        eeprom_value, success = read_register(ACS37800_REGISTER_EEPROM_0F, ACS37800_DEFAULT_I2C_ADDRESS)
        time.sleep_ms(100)
        print(" registrador 0F: ", success);print("eeprom_value: ", eeprom_value)
        if bypass:                                     # Quando bypass_n_en = 1:
            new_eeprom = eeprom_value | (1 << 24)      # ⚡ Frequência MÁXIMA de amostragem
            print("new_eeprom True: ",hex(new_eeprom)) # 🚀 Menor latência, maior responsividade
        else:                                          # 🔋 Maior consumo de energia
            new_eeprom = eeprom_value & ~(1 << 24)
            print("new_eeprom False: ",new_eeprom)
        retorno = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_EEPROM_0F, new_eeprom)
    time.sleep_ms(100)
    print(retorno)# 6. Lock
    error = write_register(ACS37800_DEFAULT_I2C_ADDRESS, ACS37800_REGISTER_VOLATILE_2F, 0x0)
    time.sleep_ms(100)
    print(error)  
    # Quando bypass_n_en = 0:  
    # 📊 Frequência controlada pelo divisor 'N'
    # 💾 Menor consumo de energia
    # ⏱️ Amostragem em intervalos controlados
def read_instantaneous():
    # Read register 2A
    data, success = read_register( ACS37800_REGISTER_VOLATILE_2A, ACS37800_DEFAULT_I2C_ADDRESS)
    time.sleep_ms(100)
    print(" data: ", data); print(" success: ", success);
    if not success:
        print("aqui")
        #return 0.0, 0.0, 0.0, False

    # Extract vcodes (signed 16-bit, assume lower 16 bits)
    vcodes = data & 0xFFFF
    if vcodes & 0x8000:  # Sign extend if negative
        vcodes -= 0x10000
    volts = vcodes / 27500.0 * 250 / 1000  # Convert to volts
    resistor_multiplier = (ACS37800_DEFAULT_DIVIDER_RES + ACS37800_DEFAULT_SENSE_RES) / ACS37800_DEFAULT_SENSE_RES
    print(" resistor_multiplier: ", resistor_multiplier)
    volts *= resistor_multiplier

    # Extract icodes (signed 16-bit, assume upper 16 bits)
    icodes = (data >> 16) & 0xFFFF
    if icodes & 0x8000:  # Sign extend if negative
        icodes -= 0x10000
    amps = icodes / 27500.0 * ACS37800_DEFAULT_CURRENT_RANGE  # Convert to amps

    # Read register 2C
    data, success1 = read_register(ACS37800_REGISTER_VOLATILE_2C, ACS37800_DEFAULT_I2C_ADDRESS)
    time.sleep_ms(100)
    print(" data1: ", data); print(" success1: ", success);
    #if not success:
        #return 0.0, 0.0, 0.0, False# Extract pinstant (signed 16-bit, assume lower 16 bits)
    pinstant = data & 0xFFFF
    print(" pinstant: ", pinstant)
    x = pinstant & 0x8000
    print(" pinstant: ", pinstant)
    if x:  # Sign extend if negative
        pinstant -= 0x10000
    lsb_per_mw = 3.08 * (30.0 / ACS37800_DEFAULT_CURRENT_RANGE)  # Adjust for sensor version
    power = pinstant / lsb_per_mw * resistor_multiplier / 1000  # Convert to watts
    print(" pinstant: ", pinstant)
    print(" volts: ", volts)
    print(" amps: ", amps)
    print(" watt: ", power)
    return volts, amps, power, True

setNumberOfSamples(1023, True)
set_bypass_n_enable(True, True)
volts, amps, watt, erro = read_instantaneous()
