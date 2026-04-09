#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module cryptographique pour RedForge
Fonctions de chiffrement, hachage, encodage et opérations APT
Version avec support furtif, APT et utilitaires avancés
"""

import hashlib
import base64
import secrets
import string
import os
import re
import hmac
import json
from typing import Dict, Any, Optional, Tuple, Union, List
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class CryptoUtils:
    """Utilitaires cryptographiques avancés avec support APT"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialise les utilitaires crypto
        
        Args:
            key: Clé de chiffrement (générée automatiquement si non fournie)
        """
        if key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = key
        self.cipher = Fernet(self.key)
        self.stealth_mode = False
        self.apt_mode = False
    
    def set_stealth_mode(self, enabled: bool):
        """Active/désactive le mode furtif"""
        self.stealth_mode = enabled
    
    def set_apt_mode(self, enabled: bool):
        """Active/désactive le mode APT"""
        self.apt_mode = enabled
    
    # ========================================
    # Hachage
    # ========================================
    
    @staticmethod
    def hash_md5(data: str) -> str:
        """Hash MD5"""
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def hash_sha1(data: str) -> str:
        """Hash SHA1"""
        return hashlib.sha1(data.encode()).hexdigest()
    
    @staticmethod
    def hash_sha256(data: str) -> str:
        """Hash SHA256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def hash_sha512(data: str) -> str:
        """Hash SHA512"""
        return hashlib.sha512(data.encode()).hexdigest()
    
    @staticmethod
    def hash_blake2b(data: str) -> str:
        """Hash BLAKE2b"""
        return hashlib.blake2b(data.encode()).hexdigest()
    
    @staticmethod
    def hash_blake2s(data: str) -> str:
        """Hash BLAKE2s"""
        return hashlib.blake2s(data.encode()).hexdigest()
    
    @staticmethod
    def hash_file(filepath: str, algorithm: str = "sha256") -> str:
        """
        Calcule le hash d'un fichier
        
        Args:
            filepath: Chemin du fichier
            algorithm: Algorithme de hash (md5, sha1, sha256, sha512, blake2b)
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        hash_obj = hash_func()
        
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def hash_hmac(key: bytes, data: bytes, algorithm: str = "sha256") -> str:
        """
        HMAC (Hash-based Message Authentication Code)
        
        Args:
            key: Clé secrète
            data: Données
            algorithm: Algorithme (md5, sha1, sha256, sha512)
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        return hmac.new(key, data, hash_func).hexdigest()
    
    # ========================================
    # Chiffrement symétrique
    # ========================================
    
    def encrypt(self, data: str) -> str:
        """
        Chiffre des données avec Fernet
        
        Args:
            data: Données à chiffrer
        """
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Déchiffre des données avec Fernet
        
        Args:
            encrypted_data: Données chiffrées
        """
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def encrypt_aes(data: bytes, key: bytes) -> bytes:
        """
        Chiffrement AES-CBC
        
        Args:
            data: Données à chiffrer
            key: Clé (16, 24 ou 32 bytes)
        """
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Padding PKCS7
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted
    
    @staticmethod
    def decrypt_aes(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Déchiffrement AES-CBC
        
        Args:
            encrypted_data: Données chiffrées (IV + ciphertext)
            key: Clé (16, 24 ou 32 bytes)
        """
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Supprimer le padding PKCS7
        pad_len = decrypted[-1]
        return decrypted[:-pad_len]
    
    @staticmethod
    def encrypt_aes_gcm(data: bytes, key: bytes) -> bytes:
        """
        Chiffrement AES-GCM (authentifié)
        
        Args:
            data: Données à chiffrer
            key: Clé (16, 24 ou 32 bytes)
        """
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        encrypted = encryptor.update(data) + encryptor.finalize()
        return iv + encrypted + encryptor.tag
    
    @staticmethod
    def decrypt_aes_gcm(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Déchiffrement AES-GCM
        
        Args:
            encrypted_data: Données chiffrées (IV + ciphertext + tag)
            key: Clé (16, 24 ou 32 bytes)
        """
        iv = encrypted_data[:12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[12:-16]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    # ========================================
    # Chiffrement asymétrique
    # ========================================
    
    @classmethod
    def encrypt_rsa(cls, data: bytes, public_key_pem: bytes) -> bytes:
        """
        Chiffrement RSA
        
        Args:
            data: Données à chiffrer
            public_key_pem: Clé publique au format PEM
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted
    
    @classmethod
    def decrypt_rsa(cls, encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """
        Déchiffrement RSA
        
        Args:
            encrypted_data: Données chiffrées
            private_key_pem: Clé privée au format PEM
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted
    
    # ========================================
    # Dérivation de clés
    # ========================================
    
    @staticmethod
    def derive_key_pbkdf2(password: str, salt: bytes = None, 
                          iterations: int = 100000, length: int = 32) -> Tuple[bytes, bytes]:
        """
        Dérive une clé avec PBKDF2
        
        Args:
            password: Mot de passe
            salt: Sel (généré si None)
            iterations: Nombre d'itérations
            length: Longueur de la clé
            
        Returns:
            (clé, sel)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    @staticmethod
    def derive_key_scrypt(password: str, salt: bytes = None,
                          n: int = 16384, r: int = 8, p: int = 1,
                          length: int = 32) -> Tuple[bytes, bytes]:
        """
        Dérive une clé avec Scrypt (plus sécurisé que PBKDF2)
        
        Args:
            password: Mot de passe
            salt: Sel (généré si None)
            n: Paramètre CPU/memory cost
            r: Taille de bloc
            p: Parallélisme
            length: Longueur de la clé
            
        Returns:
            (clé, sel)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = Scrypt(
            salt=salt,
            length=length,
            n=n,
            r=r,
            p=p,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    # ========================================
    # Encodage
    # ========================================
    
    @staticmethod
    def encode_base64(data: str) -> str:
        """Encode en base64"""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decode_base64(data: str) -> str:
        """Décode du base64"""
        return base64.b64decode(data.encode()).decode()
    
    @staticmethod
    def encode_base64_url(data: str) -> str:
        """Encode en base64 URL-safe"""
        return base64.urlsafe_b64encode(data.encode()).decode().rstrip('=')
    
    @staticmethod
    def decode_base64_url(data: str) -> str:
        """Décode du base64 URL-safe"""
        # Ajouter le padding si nécessaire
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data).decode()
    
    @staticmethod
    def encode_url(data: str) -> str:
        """Encode URL"""
        import urllib.parse
        return urllib.parse.quote(data, safe='')
    
    @staticmethod
    def decode_url(data: str) -> str:
        """Décode URL"""
        import urllib.parse
        return urllib.parse.unquote(data)
    
    @staticmethod
    def encode_hex(data: str) -> str:
        """Encode en hexadécimal"""
        return data.encode().hex()
    
    @staticmethod
    def decode_hex(data: str) -> str:
        """Décode de l'hexadécimal"""
        return bytes.fromhex(data).decode()
    
    @staticmethod
    def rot13(data: str) -> str:
        """Chiffrement ROT13"""
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def xor_encrypt(data: bytes, key: bytes) -> bytes:
        """Chiffrement XOR"""
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
    
    # ========================================
    # Génération
    # ========================================
    
    @staticmethod
    def generate_random_string(length: int = 32, 
                              include_special: bool = False,
                              include_digits: bool = True) -> str:
        """
        Génère une chaîne aléatoire
        
        Args:
            length: Longueur de la chaîne
            include_special: Inclure des caractères spéciaux
            include_digits: Inclure des chiffres
        """
        chars = string.ascii_letters
        if include_digits:
            chars += string.digits
        if include_special:
            chars += string.punctuation
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_api_key() -> str:
        """Génère une clé API"""
        return CryptoUtils.generate_random_string(32, False)
    
    @staticmethod
    def generate_token() -> str:
        """Génère un token de session"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_secure_token(length: int = 64) -> str:
        """Génère un token sécurisé"""
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_password(length: int = 16, 
                         min_lower: int = 1,
                         min_upper: int = 1,
                         min_digits: int = 1,
                         min_special: int = 0) -> str:
        """
        Génère un mot de passe sécurisé
        
        Args:
            length: Longueur du mot de passe
            min_lower: Minimum de minuscules
            min_upper: Minimum de majuscules
            min_digits: Minimum de chiffres
            min_special: Minimum de caractères spéciaux
        """
        if length < min_lower + min_upper + min_digits + min_special:
            length = min_lower + min_upper + min_digits + min_special
        
        password = []
        
        # Ajouter les caractères requis
        password.extend(secrets.choice(string.ascii_lowercase) for _ in range(min_lower))
        password.extend(secrets.choice(string.ascii_uppercase) for _ in range(min_upper))
        password.extend(secrets.choice(string.digits) for _ in range(min_digits))
        password.extend(secrets.choice(string.punctuation) for _ in range(min_special))
        
        # Remplir le reste
        remaining = length - len(password)
        chars = string.ascii_letters + string.digits
        if min_special > 0:
            chars += string.punctuation
        
        password.extend(secrets.choice(chars) for _ in range(remaining))
        
        # Mélanger
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @classmethod
    def generate_key(cls) -> bytes:
        """Génère une clé Fernet"""
        return Fernet.generate_key()
    
    @classmethod
    def generate_rsa_keypair(cls, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Génère une paire de clés RSA
        
        Args:
            key_size: Taille de la clé (2048, 3072, 4096)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @classmethod
    def generate_ecc_keypair(cls, curve: str = "SECP256R1") -> Tuple[bytes, bytes]:
        """
        Génère une paire de clés ECC (Elliptic Curve Cryptography)
        
        Args:
            curve: Courbe elliptique (SECP256R1, SECP384R1, SECP521R1)
        """
        from cryptography.hazmat.primitives.asymmetric import ec
        
        curves = {
            "SECP256R1": ec.SECP256R1(),
            "SECP384R1": ec.SECP384R1(),
            "SECP521R1": ec.SECP521R1()
        }
        
        curve_obj = curves.get(curve, ec.SECP256R1())
        private_key = ec.generate_private_key(curve_obj, default_backend())
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    # ========================================
    # Détection de type de hash
    # ========================================
    
    @staticmethod
    def detect_hash_type(hash_string: str) -> Optional[str]:
        """
        Détecte le type de hash
        
        Args:
            hash_string: Hash à analyser
        """
        hash_string = hash_string.strip()
        length = len(hash_string)
        
        patterns = {
            'md5': (32, r'^[a-f0-9]{32}$'),
            'sha1': (40, r'^[a-f0-9]{40}$'),
            'sha256': (64, r'^[a-f0-9]{64}$'),
            'sha384': (96, r'^[a-f0-9]{96}$'),
            'sha512': (128, r'^[a-f0-9]{128}$'),
            'blake2b': (128, r'^[a-f0-9]{128}$'),
            'blake2s': (64, r'^[a-f0-9]{64}$'),
            'ntlm': (32, r'^[a-f0-9]{32}$'),
            'mysql': (41, r'^\*[A-F0-9]{40}$'),
            'postgres': (32, r'^md5[a-f0-9]{32}$'),
        }
        
        for hash_type, (expected_len, pattern) in patterns.items():
            if length == expected_len and re.match(pattern, hash_string, re.IGNORECASE):
                return hash_type
        
        # Vérifier base64
        try:
            decoded = base64.b64decode(hash_string)
            if len(decoded) in [16, 20, 32, 48, 64]:
                return 'base64'
        except:
            pass
        
        return None
    
    # ========================================
    # Chiffrement APT (discret)
    # ========================================
    
    def encrypt_stealth(self, data: str, passphrase: str) -> str:
        """
        Chiffrement discret pour opérations APT
        
        Args:
            data: Données à chiffrer
            passphrase: Phrase de passe
        """
        # Dériver une clé
        key, salt = self.derive_key_pbkdf2(passphrase, iterations=10000)
        
        # Chiffrer
        encrypted = self.encrypt_aes_gcm(data.encode(), key[:32])
        
        # Encoder en base64
        result = base64.b64encode(salt + encrypted).decode()
        return result
    
    def decrypt_stealth(self, encrypted_data: str, passphrase: str) -> str:
        """
        Déchiffrement discret pour opérations APT
        
        Args:
            encrypted_data: Données chiffrées
            passphrase: Phrase de passe
        """
        data = base64.b64decode(encrypted_data)
        salt = data[:16]
        ciphertext = data[16:]
        
        # Dériver la clé
        key = self.derive_key_pbkdf2(passphrase, salt, iterations=10000)[0]
        
        # Déchiffrer
        decrypted = self.decrypt_aes_gcm(ciphertext, key[:32])
        return decrypted.decode()
    
    # ========================================
    # Serialisation sécurisée
    # ========================================
    
    def secure_json_dumps(self, data: Dict, encrypt: bool = True) -> str:
        """
        Sérialise JSON de manière sécurisée (optionnellement chiffré)
        
        Args:
            data: Données à sérialiser
            encrypt: Chiffrer les données
        """
        json_str = json.dumps(data, ensure_ascii=False)
        if encrypt:
            return self.encrypt(json_str)
        return base64.b64encode(json_str.encode()).decode()
    
    def secure_json_loads(self, data: str, encrypted: bool = True) -> Dict:
        """
        Désérialise JSON de manière sécurisée
        
        Args:
            data: Données sérialisées
            encrypted: Les données sont chiffrées
        """
        if encrypted:
            json_str = self.decrypt(data)
        else:
            json_str = base64.b64decode(data).decode()
        return json.loads(json_str)
    
    # ========================================
    # Signature et vérification
    # ========================================
    
    @staticmethod
    def sign_data(data: bytes, private_key_pem: bytes) -> bytes:
        """
        Signe des données avec une clé privée RSA
        
        Args:
            data: Données à signer
            private_key_pem: Clé privée au format PEM
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    @staticmethod
    def verify_signature(data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """
        Vérifie une signature
        
        Args:
            data: Données originales
            signature: Signature à vérifier
            public_key_pem: Clé publique au format PEM
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False


# Instance globale
crypto = CryptoUtils()


# Fonctions de commodité
def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA256"""
    return CryptoUtils.hash_sha256(password)


def verify_password(password: str, hash_value: str) -> bool:
    """Vérifie un mot de passe"""
    return CryptoUtils.hash_sha256(password) == hash_value


def generate_secure_token() -> str:
    """Génère un token sécurisé"""
    return CryptoUtils.generate_secure_token()


if __name__ == "__main__":
    print("=" * 60)
    print("Test des utilitaires crypto")
    print("=" * 60)
    
    # Hash
    print(f"\n🔐 Hachage:")
    print(f"  MD5: {CryptoUtils.hash_md5('test')}")
    print(f"  SHA256: {CryptoUtils.hash_sha256('test')}")
    print(f"  BLAKE2b: {CryptoUtils.hash_blake2b('test')}")
    
    # Chiffrement
    print(f"\n🔒 Chiffrement:")
    crypto_test = CryptoUtils()
    encrypted = crypto_test.encrypt("Message secret")
    print(f"  Chiffré (Fernet): {encrypted}")
    decrypted = crypto_test.decrypt(encrypted)
    print(f"  Déchiffré: {decrypted}")
    
    # Génération
    print(f"\n🎲 Génération:")
    print(f"  Mot de passe: {CryptoUtils.generate_password()}")
    print(f"  Mot de passe fort: {CryptoUtils.generate_password(length=24, min_special=2)}")
    print(f"  Token: {CryptoUtils.generate_token()}")
    print(f"  Clé API: {CryptoUtils.generate_api_key()}")
    
    # Détection de hash
    print(f"\n🔍 Détection:")
    test_hash = CryptoUtils.hash_md5("test")
    print(f"  Hash: {test_hash}")
    print(f"  Type détecté: {CryptoUtils.detect_hash_type(test_hash)}")
    
    # Mode APT
    print(f"\n🎭 Mode APT:")
    crypto_test.set_apt_mode(True)
    stealth_enc = crypto_test.encrypt_stealth("Donnée sensible", "passphrase_secrète")
    print(f"  Chiffré APT: {stealth_enc[:50]}...")
    stealth_dec = crypto_test.decrypt_stealth(stealth_enc, "passphrase_secrète")
    print(f"  Déchiffré APT: {stealth_dec}")
    
    # JSON sécurisé
    print(f"\n📦 JSON sécurisé:")
    data = {"user": "admin", "role": "administrator"}
    secure_json = crypto_test.secure_json_dumps(data)
    print(f"  JSON chiffré: {secure_json[:50]}...")
    decoded = crypto_test.secure_json_loads(secure_json)
    print(f"  JSON déchiffré: {decoded}")
    
    print("\n✅ Tests terminés")