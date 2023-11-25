AES = {};
AES.BITS = 256;

AES.encrypt = function(data, key) {
  try {
    // Convertir la clave a un formato adecuado para sjcl
    var sjclKey = sjcl.codec.utf8String.toBits(key);

    // Convertir los datos a un formato adecuado para sjcl
    var sjclData = sjcl.codec.utf8String.toBits(data);

    // Encriptar usando AES
    var encrypted = sjcl.encrypt(sjclKey, sjclData);
  } catch (error) {
    console.error("Error encriptando los datos:", error);
  }
  return encrypted;
};