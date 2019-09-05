import grovepi
import time
import smtplib
import time
import requests


dht_sensor_port=4 # DHT11 uses digital ports connected to I2C ports so change this for your preference. (We used D4 port.)
dht_sensor_type=0 # 0 for DHT11, 1 for DHT22.


temp_high_alert=25.0 # Change this depending on how hot or cold the room you think should be for the program to send email alerts.
hum_high_alert=35  # Change this depending on how hot or cold the room you think should be for the program to send email alerts.
temp_low_alert=15.0  # Change this depending on how hot or cold the room you think should be for the program to send email alerts.
hum_low_alert=15  # Change this depending on how hot or cold the room you think should be for the program to send email alerts.

source_mail_address='yourmail@gmail.com' # Your mail address that you will be sending the mail from.
target_mail_address='targetmail@gmail.com' # Destination mail address.
source_mail_password='passwd' # Password of your mail address for logging in.


# This is taken from https://www.freecodecamp.org/forum/t/make-a-script-read-gps-geolocation/241607/2
ip_request = requests.get('https://get.geojs.io/v1/ip.json')
my_ip = ip_request.json()['ip']  
#print(my_ip)


geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + my_ip + '.json'
geo_request = requests.get(geo_request_url)
geo_data = geo_request.json()

geojs_data=geo_data["organization"] # We store the geojs data in a variable called geojs_data.

# Instead of organization you can use either of below whichever you need for that instance.
# "area_code"
# "continent_code"
# "country"
# "country_code"
# "country_code3"
# "ip"
# "latitude"
# "longitude"
# "organization"
# "timezone"

underscored_geojs_data=geojs_data.replace(" ", "_") # Since InfluxDB line protocol doesn't support spaces other than the space between tag value and field value we put underscores for the spaces found in tag value.


data=open('data.txt','w') # This is the file we create that will be sent to the influxDB database for storage. We will fill this with information below.
[ temp,hum ] = grovepi.dht(dht_sensor_port,dht_sensor_type) # Grovepi sensor function to store temperature and humidity.
print ('Temp: '+ str(temp) + '*C' + '\tHumidity:' + ' %'+ str(hum) + ' ' + str(time.strftime("%s",time.gmtime()))) # prints the data and time.

# Write the data taken into data.txt below. The format is written as it is because the line protocol is strict about the typo.
data.write('temperature,location=' + underscored_geojs_data + ' temp='+ str(temp))
data.write('\n')
data.write('temperature,location=' + underscored_geojs_data + ' hum='+ str(hum))

# Sending the mails an email.
def mail(content): # Content is defined in the if statements below, which is the message to be sent in the email.
    mail = smtplib.SMTP("smtp.gmail.com",587) 
    mail.starttls()
    mail.login(source_mail_address,source_mail_password) # Enters your mail for mails to be sent.
    mail.sendmail(source_mail_address,target_mail_address,content) # #nters the source address, target address and content to be sent for the sendmail function to work. Content is defined lower

# Send mail depending on the room temperature and humidity.
if temp>=temp_high_alert: 
    content = 'Room temperature ' + str(temp) + '*C' + ', Temperature is too high!'
    mail(content)
elif temp<=temp_low_alert:
    content = 'Room temperature ' + str(temp) + '*C' + ', It is  advised to increase the temperature.'
    mail(content)
elif hum >=hum_high_alert:
    content = 'Humidity inside the room  %' +  str(hum)  + ', Humidity is too high!'
    mail(content)
elif hum <=hum_low_alert:
    content = 'Humidity inside the room  %' +  str(hum)  + ', Humidity is too low!'
    mail(content)
