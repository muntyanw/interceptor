api_id = 24364263  #25965329
api_hash = "1f03c4f0e8617dd5fe4f16e9d629f47c" #"6604012087bc1273f1f918571c02af24"

#каналы которые слушаем#
channels_to_listen = {
    # 1603064946: {#InterTest
    #     'moderation_if_image': True,
    #     'auto_moderation_and_send_text_message': True,
    #     'replacements': {
    #         'слово1': 'замена1',
    #         'слово2': 'замена2',
    #         'слово3': 'замена3',
    #         'слово4': 'замена4',
    #     }
    # },
    2183790519: {#Sender
        'moderation_if_image': False,
        'auto_moderation_and_send_text_message': True,
        'replacements': {
            'слово1': 'замена1',
            'слово2': 'замена2',
            'слово3': 'замена3',
            'слово4': 'замена4',
        }
    },
    1242446516: {#Україна 24/7
        'moderation_if_image': False,
        'auto_moderation_and_send_text_message': True,
        'replacements': {
            'слово1': 'замена1',
            'слово2': 'замена2',
            'слово3': 'замена3',
            'слово4': 'замена4',
        }
    },
    1363028986: {#Український Чат 24/7
        'moderation_if_image': False,
        'auto_moderation_and_send_text_message': True,
        'replacements': {
            'слово1': 'замена1',
            'слово2': 'замена2',
            'слово3': 'замена3',
            'слово4': 'замена4',
        }
    },
    4508196790: {#Український Чат 24/7
        'moderation_if_image': False,
        'auto_moderation_and_send_text_message': True,
        'replacements': {
            'слово1': 'замена1',
            'слово2': 'замена2',
            'слово3': 'замена3',
            'слово4': 'замена4',
        }
    },
    # 1229342507: {#КЛИЕНТЫ || РАБОТА ОНЛАЙН
    #     'moderation_if_image': False,
    #     'auto_moderation_and_send_text_message': True,
    #     'replacements': {
    #         'слово1': 'замена1',
    #         'слово2': 'замена2',
    #         'слово3': 'замена3',
    #         'слово4': 'замена4',
    #     }
    # },
    2023070684: { #Crypto Master | Futures Signals
        'moderation_if_image': False,
        'auto_moderation_and_send_text_message': True, #если это значение труе то будет производить автозамену и отсылать, если фэлз будет делать автозамену и отсылать на сайт человеку
        'replacements': {
            'bingx': 'google',
            'SamCrypto_Master': 'parampan',
           
        },
        
    },
}


#каналы куда отсылаем#
channels_to_send = [2204843457] #2170620330
