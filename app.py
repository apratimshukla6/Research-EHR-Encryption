from flask import Flask, render_template, url_for, request, redirect
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from Cryptodome.Cipher import AES
from hashlib import blake2b
import base64
import os

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
app.config['SECRET_KEY'] = 'abc123@567$#'

def GenerateSign(string, secret, read_key=None, write_key=None, delete_key=None, read=False, write=False, delete=False):
    key = bytes(secret, 'utf-8')
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(bytes(string, 'utf-8'))
    
    encrypted_read = None
    encrypted_write = None
    encrypted_delete = None
    concat = {}
    
    if(read):
        encrypted_read = bytes(read_key, 'utf-8')
        cipher_read = AES.new(encrypted_read, AES.MODE_EAX)
        nonce_read = cipher_read.nonce
        ciphertext_read, tag_read = cipher_read.encrypt_and_digest(bytes(secret, 'utf-8'))
        concat["read"] = str(base64.b64encode(ciphertext_read),'utf-8')
        
    if(write):
        encrypted_write = bytes(write_key, 'utf-8')
        cipher_write = AES.new(encrypted_write, AES.MODE_EAX)
        nonce_write = cipher_write.nonce
        ciphertext_write, tag_write = cipher_write.encrypt_and_digest(bytes(secret, 'utf-8'))
        concat["write"] = str(base64.b64encode(ciphertext_write),'utf-8')
    
    if(delete):
        encrypted_delete = bytes(delete_key, 'utf-8')
        cipher_delete = AES.new(encrypted_delete, AES.MODE_EAX)
        nonce_delete = cipher_delete.nonce
        ciphertext_delete, tag_delete = cipher_delete.encrypt_and_digest(bytes(secret, 'utf-8'))
        concat["delete"] = str(base64.b64encode(ciphertext_delete),'utf-8')
        
    hash_value = bytes(str(concat), 'utf-8')
        
    hashed = blake2b(hash_value).hexdigest()
    
    private_key = Ed25519PrivateKey.generate()
    signature = private_key.sign(bytes(hashed, 'utf-8'))
    public_key = private_key.public_key()
    
    encoded_signature = str(base64.b64encode(signature),'utf-8')
    
    #public_key.verify(encoded_signature, b"The hashed value generated")
    
    return (encoded_signature, concat)


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        text = request.form['data']
        key = request.form['key']
        read_key = request.form['read']
        write_key = request.form['write']
        delete_key = request.form['delete']
        
        read = False
        write = False
        delete = False
        
        if(read_key!=''):
            read = True
            
        if(write_key!=''):
            write = True
            
        if(delete_key!=''):
            delete = True
        
        encoded_signature, concat = GenerateSign(text, key, read_key=read_key, write_key=write_key, delete_key=delete_key, read=read, write=write, delete=delete)
        
        read_ciphered_key = ""
        write_ciphered_key = ""
        delete_ciphered_key = ""
        
        if(read_key!=''):
            read_ciphered_key = concat["read"]
        
        if(write_key!=''):
            write_ciphered_key = concat["write"]
        
        if(delete_key!=''):
            delete_ciphered_key = concat["delete"]
        
        return render_template('output.html', encoded_signature = encoded_signature, read_ciphered_key = read_ciphered_key, write_ciphered_key = write_ciphered_key, delete_ciphered_key = delete_ciphered_key)
    
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)