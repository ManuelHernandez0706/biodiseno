from pyrebase import pyrebase
import datetime

config = {
    "apiKey": "AIzaSyCnrahVCBhNQxKjlvusAaKXyEvT-i25GtA",
    "authDomain": "fundamentos-de-biodiseno.firebaseapp.com",
    "databaseURL": "https://fundamentos-de-biodiseno.firebaseio.com",
    "projectId": "fundamentos-de-biodiseno",
    "storageBucket": "fundamentos-de-biodiseno.appspot.com",
    "messagingSenderId": "168366607778",
    "appId": "1:168366607778:web:eebc0b56843125cde8f6fb",
    "measurementId": "G-CQWN7CX531"
   }
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth=firebase.auth()

class Database:
    usuario = ""
    def add_user(self, correo, nombre, clave, numero):
        try:
            datos = db.child("medicos").get()
            a=0
            for celular in datos.each():
                if celular.val()['celular']==numero:
                    a = -2
            if a == -2:
                return a
            else:    
                for usuarios in datos.each():
                    if usuarios.key() == nombre:
                        a==-1
                if a==-1:
                    return a
                else:  
                    auth.create_user_with_email_and_password(correo, clave)
                    print("Succesfully created account")
                    n = {"celular": numero, "correo": correo}
                    db.child('medicos').child(nombre).set(n)
                    return a
        except:
            return -3
        
    def iniciar_sesion(self, email, clave):
        a=1
        try:
            login = auth.sign_in_with_email_and_password(email, clave)
            self.usuario = login
            a = 1
        except:
            a = -10
        return a
        
    def get_user(self, email):
        datos = db.child("medicos").get()
        for usuarios in datos.each():
            if usuarios.val()['correo']==email:
                return usuarios.key()
                break
            
    def cambiar_clave(self, clave, email):
        auth.delete_user_account(self.usuario['idToken'])
        auth.create_user_with_email_and_password(email, clave)
    
    def validate_existent(self, user, numero, correo):
        datos = db.child("medicos").get()
        a = -1
        for usuarios in datos.each():
            if usuarios.key() == user:
                if usuarios.val()['correo']== correo and usuarios.val()['celular'] == numero:
                    a == 1
        return a
    
    def reset_account(self, email):
        auth.send_password_reset_email(email)
    
    def get_number(self, user):
        datos = db.child("medicos").get()
        for usuarios in datos.each():
            if usuarios.key() == user:
                cellphone = usuarios.val()['celular']
        return cellphone
    
    def guardar_resultados(self, paciente, users, edad, peso, talla, sexo, fractura, fuma, t_score1, t_score2, valor_dmo1, valor_dmo2):
        fecha = self.get_date()
        n = {"edad":edad,"peso":peso,"talla":talla,"sexo":sexo,"fractura":fractura,"fuma":fuma,"T-Score Cuello Femoral":t_score1, "T-Score Columna Vertebral":t_score2, "DMO Cuello Femoral":valor_dmo1, "DMO Columna Vertebral":valor_dmo2, "Fecha":fecha}
        numeros_tomas = self.Obtener_Numero_Tomas(paciente)
        if numeros_tomas == -1:
            db.child("medicos").child(users).child("pacientes atendidos").child(paciente).child("Toma 1").set(n)
            db.child("pacientes").child(paciente).child("Toma 1").set(n)
        else:
            toma = "Toma " + str(numeros_tomas+1)
            db.child("medicos").child(users).child("pacientes atendidos").child(paciente).child(toma).set(n)
            db.child("pacientes").child(paciente).child(toma).set(n)
            
    def Borrar_Registro(self, medico, paciente):
        num_tomas = self.Obtener_Numero_Tomas(paciente)
        toma = "Toma " + str(num_tomas)
        db.child("medicos").child(medico).child("pacientes atendidos").child(paciente).child(toma).remove()
        db.child("pacientes").child(paciente).child(toma).remove()
        return 1
    
    def Obtener_Numero_Tomas(self, paciente):
        try:
            a = 0
            tomas = db.child("pacientes").child(paciente).get()
            for n in tomas.val():
                a = a+1
            return a
        except:
            return -1
        
    def get_amount_pacients(self, medico):
        try:
            datos = db.child("medicos").child(medico).child("pacientes atendidos").get()
            cant = 0
            for n in datos.each():
                cant +=1
            return cant
        except:
            return -1
        
    def get_name_pacient(self, medico, i):
        datos = db.child("medicos").child(medico).child("pacientes atendidos").get()
        pacientes = []
        for n in datos.each():
            pacientes.append(n.key())
        return pacientes[i]
    
    def get_edad(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("edad").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("edad").get()
            return datos.val()
    
    def get_dmo1(self, paciente, registro):
        datos = db.child("pacientes").child(paciente).child(registro).child("DMO Cuello Femoral").get()
        return datos.val()
    
    def get_dmo2(self, paciente, registro):
        datos = db.child("pacientes").child(paciente).child(registro).child("DMO Columna Vertebral").get()
        return datos.val()
    
    def get_peso(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("peso").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("peso").get()
            return datos.val()
        
    def get_t_score2(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("T-Score Columna Vertebral").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("T-Score Columna Vertebral").get()
            return datos.val()
        
    def get_t_score1(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("T-Score Cuello Femoral").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("T-Score Cuello Femoral").get()
            return datos.val()
    
    def get_fractura(self, paciente, registro):
        if(registro == "Toma 0"):
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("fractura").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("fractura").get()
            return datos.val()
    
    def get_talla(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("talla").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("talla").get()
            return datos.val()
    
    def get_sexo(self, paciente, registro):
        if registro == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            toma = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(toma).child("sexo").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(registro).child("sexo").get()
            return datos.val()
    
    def get_fuma(self, paciente):
        numeros_tomas = self.Obtener_Numero_Tomas(paciente)
        toma = "Toma " + str(numeros_tomas)
        datos = db.child("pacientes").child(paciente).child(toma).child("fuma").get()
        return datos.val()
        
    def validar_paciente(self, dni):
        a = 0
        datos = db.child("pacientes").get()
        for n in datos.each():
            if n.key() == dni:
                a = 1
        return a
    
    def get_medico(self, dni):
        datos = db.child("medicos").get()
        b= ""
        for n in datos.each():
            a = n.key()
            try:
                datos2 = db.child("medicos").child(a).child("pacientes atendidos").get()
                for k in datos2.each():
                    try:
                        if k.key() == dni:
                            b = n.key()
                    except:
                        pass
            except:
                pass
        return b
    
    def validar_paciente_con_medico(self, medico, paciente):
        a = 0
        try:
            datos = db.child("medicos").child(medico).child("pacientes atendidos").get()
            for n in datos.each():
                if n.key() == paciente:
                    a = 1
        except:
            pass
        return a
        
    def get_correo_medico(self, medico):
        datos = db.child("medicos").child(medico).child("correo").get()
        return datos.val()
    
    def get_celular_medico(self, medico):
        datos = db.child("medicos").child(medico).child("celular").get()
        return datos.val()
    
    def get_date_toma(self, paciente, toma):
        if toma == "Toma 0":
            numeros_tomas = self.Obtener_Numero_Tomas(paciente)
            registro = "Toma " + str(numeros_tomas)
            datos = db.child("pacientes").child(paciente).child(registro).child("Fecha").get()
            return datos.val()
        else:
            datos = db.child("pacientes").child(paciente).child(toma).child("Fecha").get()
            return datos.val()
        
       
    
    def get_date(self):
        return str(datetime.datetime.now()).split(" ")[0]
