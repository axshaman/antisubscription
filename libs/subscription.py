import base64
import re

def subscription(raw_data_of_mail, keys_list) -> str:                       # Find mail body content
        main_content : str = raw_data_of_mail[                   # We are getting MC by taking last string of Raw Data
            raw_data_of_mail.find('X-Antivirus-Status:') +       # plus Length of this string 
            len('X-Antivirus-Status: Clean') : ]            
        
        try:
            b = base64.b64decode(main_content)
            s = b.decode("utf-8")
            main_content = s
        except: main_content
        
        def scan_text_latin(keys_list):
            # print(' --- scan_text_latin - START ---')
            
            # Calculate key values to create probability of Subscription
            subscription_count_mention : int = 0

            
            for value in keys_list:
                subscr = re.findall(value, main_content)

                if len(subscr) > 0 :
                    for sub in range(len(subscr)):
                        subscription_count_mention += 1
                else:
                    # print( "We didn't find any matches in this letter." )  
                    pass
                      
            # print(subscription_count_mention)
            return subscription_count_mention


        text_html : list = re.findall('text/html', raw_data_of_mail)    # Find Coding in all data
        text_plain : list = re.findall('text/plain', raw_data_of_mail)
        # print(text_plain)
        
        
        if len(text_html) > 0 or len(text_plain) > 0:            # Array of key values for searchingkeys_list
            result : int = scan_text_latin(keys_list)            # Func which will do scanning job
        else:
            result = None
            print('No coding')
        
        # print('The result of mail scanning: ', result)
        return result


if __name__ == '__main__':
    subscription()