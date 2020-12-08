from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ThreeLineListItem, TwoLineListItem
from kivy.properties import ObjectProperty
from firebase_app import Database
from kivy.core.window import Window
import math

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

Window.size = (300,500)

db = Database()

class MenuScreen(Screen):
    pass

class MedicoScreen(Screen):
    email = ObjectProperty(None)
    clave = ObjectProperty(None)
    def show_data(self):
        if db.iniciar_sesion(self.email.text, self.clave.text)==1:
            MenuMedico.email = self.email.text
            PerfilMedico.clave = self.clave.text
            PerfilMedico.email = self.email.text
            CambiarClave.email = self.email.text
            CambiarClave.clave = self.clave.text
            self.reset()
            sm.current = 'menu_medico'
        else:
            IngresoInvalido(self)
            self.reset()
            
    def reset(self):
        self.email.text = ""
        self.clave.text = ""
        pass
    def close_dialog(self,obj):
        self.dialog.dismiss()
        
class MenuMedico(Screen):
    email = ""
    bienvenida = ObjectProperty(None)
    avatar = ObjectProperty(None)
    nombre_medico = ObjectProperty(None)
    def on_enter(self):
        usuario = db.get_user(self.email)
        RegistroPacientes.usuario = usuario
        PerfilMedico.usuario = usuario
        CambiarClave.usuario = usuario
        self.bienvenida.text = "Medico " + usuario
        self.nombre_medico.text = usuario
    def toma_de_datos(self):
        usuario = db.get_user(self.email)
        TomaDatos1.usuario = usuario
        sm.current = 'toma_datos1'
    def muestra_de_pacientes(self):
        RegistroPacientes.usuario = db.get_user(self.email)
        sm.current = 'registro_pacientes'
    
    def busqueda_de_pacientes(self):
        BusquedaPacientes.usuario = db.get_user(self.email)
        sm.current = 'busqueda_pacientes'
    
    def reset(self):
        self.bienvenida.text = ""
        self.nombre_medico.text = ""
        
    def mostrar_perfil(self):
        sm.current = 'perfil_medico'
    
    def cambiar_contrasena(self):
        sm.current = 'cambiar_clave'
    
    def salir_sesion(self):
        Validar_Salir_Sesion(self)
        
    def salir(self,obj):
        self.close_dialog(self)
        self.reset()
        sm.current = 'menu'
    def close_dialog(self,obj):
        self.dialog.dismiss()

class BusquedaPacientes(Screen):
    usuario = ""
    paciente = ObjectProperty(None)
    
    def validar_ingreso(self):
        if len(self.paciente.text) == 8 and self.paciente.text.isdigit():
            if db.validar_paciente_con_medico(self.usuario, self.paciente.text) == 1:
                Toma_Paciente.usuario = self.usuario
                Toma_Paciente.paciente = self.paciente.text
                sm.current = 'toma_paciente'
                self.reset()
            else:
                check_string = 'El paciente no existe o esta registrado con otro medico'
                cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                self.dialog = MDDialog(title='Error en Paciente', text=check_string,
                        size_hint=(0.7,0.6), buttons=[cerrar_botton])
                self.dialog.open()
                self.reset()
        else:
            datos_incorrectos(self)
            self.reset()
        
    def reset(self):
        self.paciente.text = ""
    
    def close_dialog(self,obj):
        self.dialog.dismiss()

class Toma_Paciente(Screen):
    usuario = ""
    paciente = ""
    b = 0
    lista = []
    pacient = ObjectProperty(None)
    num_toma = ObjectProperty(None)
    box = ObjectProperty(None)
    
    def on_enter(self):
        self.pacient.text = "Tomas para el paciente " + self.paciente
        cant_tomas = db.Obtener_Numero_Tomas(self.paciente)
        for i in range(cant_tomas):
            toma = "Toma " + str(i + 1)
            fecha = db.get_date_toma(self.paciente, toma)
            objeto_lista = TwoLineListItem(text= toma,
                        secondary_text = 'Fecha: ' + fecha,
                        font_style = 'H6', secondary_font_style = 'Subtitle1')
            self.box.add_widget(objeto_lista)
            self.lista.append(objeto_lista)
            self.b+=1
    
    def buscar_toma(self):
        valido = 0
        for i in range(self.b):
            toma = "Toma " + str(i +1)
            if self.num_toma.text.title() == toma:
                valido = 1
        if valido==1:
            Toma_Paciente_Final.toma = self.num_toma.text.title()
            Toma_Paciente_Final.usuario = self.usuario
            Toma_Paciente_Final.paciente = self.paciente
            self.reset_all()
            sm.current = 'toma_paciente_final'
        else:
            check_string = 'Ingrese una toma valida entre las mostradas'
            cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Error en la busqueda', text=check_string,
                    size_hint=(0.7,0.6), buttons=[cerrar_botton])
            self.dialog.open()
            self.reset()
        
    def reset(self):
        self.num_toma.text = ""
        
    def reset_all(self):
        self.pacient.text = ""
        self.num_toma.text = ""
        for i in range(self.b):
            self.box.remove_widget(self.lista[i])
        self.lista = []
        self.b = 0
    
    def close_dialog(self, obj):
        self.dialog.dismiss()
    
class Toma_Paciente_Final(Screen):
    usuario = ""
    toma = ""
    paciente = ""
    fecha_toma = ObjectProperty(None)
    edad_peso_talla = ObjectProperty(None)
    t_score1 = ObjectProperty(None)
    t_score2 = ObjectProperty(None)
    fract = ObjectProperty(None)
    res_ost = ObjectProperty(None)
    label1 = ObjectProperty(None)
    label2 = ObjectProperty(None)
    
    def on_enter(self):
        self.label1.text = 'DMO/T-Score Cuello Femoral:'
        self.label2.text = 'DMO/T-Score Columna Vertebral (L1 L3):'
        fecha = db.get_date_toma(self.paciente, self.toma)
        edad = db.get_edad(self.paciente, self.toma)
        talla = db.get_talla(self.paciente, self.toma)
        peso = db.get_peso(self.paciente, self.toma)
        t_score1 = db.get_t_score1(self.paciente, self.toma)
        t_score2 = db.get_t_score2(self.paciente, self.toma)
        fractura = db.get_fractura(self.paciente, self.toma)
        dmo1 = db.get_dmo1(self.paciente, self.toma)
        dmo2 = db.get_dmo2(self.paciente, self.toma)
        self.fecha_toma.text = "Fecha: " + fecha
        self.edad_peso_talla.text = "Edad " + edad + ", Talla " + talla + "cm, Peso " + peso + "kg"
        self.t_score1.text = str(dmo1) + "g/cm^2    //    " + str(t_score1)
        self.t_score2.text = str(dmo2) + "g/cm^2    //    " + str(t_score2)
        if fractura == "si":
            self.fract.text = "Presenta al menos una fractura"
        else:
            self.fract.text = "No tiene fracturas actuales"
        if float(t_score1)<-2.5 or float(t_score2)<-2.5:
            if fractura == "si":
                self.res_ost.text = "Estado: El paciente tiene osteoporosis severa (con fractura)"
            else:
                self.res_ost.text = "Estado: Es paciente tiene osteoporosis"
        else:
            if float(t_score1)<-1.0 or float(t_score2)<-1.0:
                self.res_ost.text = "Estado: El paciente tiene osteopenia"
            else:
                self.res_ost.text = "Estado: El paciente se encuentra bien"
    
    def reset(self):
        self.fecha_toma.text = ""
        self.edad_peso_talla.text = ""
        self.t_score1.text = ""
        self.t_score2.text = ""
        self.fract.text = ""
        self.res_ost.text = ""
        self.label1.text = ""
        self.label2.text = ""
                
class PerfilMedico(Screen):
    email = ""
    usuario = ""
    clave = ""
    numero = ""
    medico_medico = ObjectProperty(None)
    clave_medico = ObjectProperty(None)
    celular_medico = ObjectProperty(None)
    correo = ObjectProperty(None)
    def on_enter(self):
        celular = db.get_number(self.usuario)
        self.medico_medico.text = "Medico " + self.usuario
        self.correo.text = self.email
        texto_aux = ""
        for a in range(len(self.clave)):
            texto_aux += "*"
        self.clave_medico.text = texto_aux
        self.celular_medico.text = "El celular es " + celular
    def reset(self):
        self.medico_medico.text = ""
        self.clave_medico.text = ""
        self.celular_medico.text = ""
        self.correo.text = ""
        
class CambiarClave(Screen):
    email = ""
    clave = ""
    usuario = ""
    nueva_clave_1 = ObjectProperty(None)
    nueva_clave_2 = ObjectProperty(None)
    nombre_medico = ObjectProperty(None)
    def on_enter(self):
        self.nombre_medico.text = self.usuario
    def verificar_clave(self):
        if self.nueva_clave_1.text != "" and self.nueva_clave_2.text!= "":
            if self.nueva_clave_1.text == self.nueva_clave_2.text and len(self.nueva_clave_1.text)>=6:
                if self.nueva_clave_1.text != self.clave:   
                    db.cambiar_clave(self.nueva_clave_1.text, self.email)
                    check_string = 'Se ha modificado la contraseña con exito'
                    cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                    self.dialog = MDDialog(title='Clave modificada', text=check_string,
                                                  size_hint=(0.7,0.6), buttons=[cerrar_botton])
                    self.dialog.open()
                    sm.current = 'menu_medico'
                else:
                    contrasena_repetida(self)
            else:
                if self.nueva_clave_1.text != self.nueva_clave_2.text:
                    error_contrasena(self)
                else:
                    check_string = 'La clave debe tener como minimo 6 caracteres'
                    cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                    self.dialog = MDDialog(title='Error en nueva clave', text=check_string,
                                                  size_hint=(0.7,0.6), buttons=[cerrar_botton])
                    self.dialog.open()
        else:
            invalidForm(self)
        self.reset()
    def reset(self):
        self.nueva_clave_1.text = ""
        self.nueva_clave_2.text = ""
    def regresar(self):
        self.reset()
        sm.current = 'menu_medico'
    def mostrar_perfil(self):
        self.reset()
        sm.current = 'perfil_medico'
    def salir_sesion(self):
        self.reset()
        sm.current = 'menu_medico'
        
    def close_dialog(self,obj):
        self.dialog.dismiss()
    
class TomaDatos1(Screen):
    usuario = ""
    edad = ObjectProperty(None)
    peso = ObjectProperty(None)
    talla = ObjectProperty(None)
    paciente = ObjectProperty(None)
    masculino = ObjectProperty(None)
    femenino = ObjectProperty(None)
    fractura_si = ObjectProperty(None)
    fractura_no = ObjectProperty(None)
    fuma_si = ObjectProperty(None)
    fuma_no = ObjectProperty(None)
    
    def checkbox_m(self):
        self.femenino.active = False
    def checkbox_f(self):
        self.masculino.active = False
    def checkbox_fractura_si(self):
        self.fractura_no.active = False
    def checkbox_fractura_no(self):
        self.fractura_si.active = False
    def checkbox_fumador_si(self):
        self.fuma_no.active = False
    def checkbox_fumador_no(self):
        self.fuma_si.active = False
        
    def validar_salida(self):
        ValidarRetorno(self)
   
    def siguiente_pagina(self):
        if self.edad.text != "" and self.peso.text != "" and self.paciente.text != "" and self.talla.text != "" and (self.masculino.active == True or self.femenino.active == True) and (self.fractura_si.active == True or self.fractura_no.active == True) and (self.fuma_si.active == True or self.fuma_no.active == True):
            if self.edad.text.isdigit() and self.peso.text.isdigit() and self.paciente.text.isdigit() and self.talla.text.isdigit():
                if len(self.edad.text)<=2 and float(self.peso.text)>=30 and float(self.peso.text)<=150 and len(self.paciente.text)==8 and len(self.talla.text)<=3:
                    TomaDatos2.edad = self.edad.text
                    TomaDatos2.peso = self.peso.text
                    TomaDatos2.usuario = self.usuario
                    TomaDatos2.paciente = self.paciente.text
                    TomaDatos2.talla = self.talla.text
                    if self.masculino.active == True:
                        TomaDatos2.sexo = "masculino"
                    else:
                        TomaDatos2.sexo = "femenino"
                    if self.fractura_si.active == True:
                        TomaDatos2.fractura = "si"
                    else:
                        TomaDatos2.fractura = "no"
                    if self.fuma_si.active == True:
                        TomaDatos2.fuma = "si"
                    else:
                        TomaDatos2.fuma = "no"
                    self.reset()
                    sm.current = 'toma_datos2'
                else:
                    datos_incorrectos(self)
            else:
                datos_incorrectos(self)
        else:
            invalidForm(self)
    def reset(self):
        self.edad.text = ""
        self.peso.text = ""
        self.paciente.text = ""
        self.talla.text = ""
        self.femenino.active = False
        self.masculino.active = False
        self.fractura_si.active = False
        self.fractura_no.active = False
        self.fuma_si.active = False
        self.fuma_no.active = False
    def retornar_pantalla(self, obj):
        self.close_dialog(self)
        self.reset()
        sm.current = 'menu_medico'
        
    def close_dialog(self,obj):
        self.dialog.dismiss()

class TomaDatos2(Screen):
    usuario = ""
    edad = ""
    peso = ""
    talla = ""
    paciente = ""
    sexo = ""
    fractura = ""
    fuma = ""
    t_score1 = ObjectProperty(None)
    t_score2 = ObjectProperty(None)
    valor_dmo1 = ObjectProperty(None)
    valor_dmo2 = ObjectProperty(None)
    
    def ingresar_datos(self):
        a = len(self.t_score1.text)
        b = len(self.t_score2.text)
        c = len(self.valor_dmo1.text)
        d = len(self.valor_dmo2.text)
        cant_digitos1 = 0
        cant_digitos2 = 0
        cant_digitos3 = 0
        cant_digitos4 = 0
        for digito in self.t_score1.text:
            if digito.isdigit() or digito=='.' or digito=='-':
                cant_digitos1+=1
        for digito in self.t_score2.text:
            if digito.isdigit() or digito=='.' or digito=='-':
                cant_digitos2 +=1
        for digito in self.valor_dmo1.text:
            if digito.isdigit() or digito=='.' or digito=='-':
                cant_digitos3 +=1
        for digito in self.valor_dmo2.text:
            if digito.isdigit() or digito=='.' or digito=='-':
                cant_digitos4 +=1
        if a==cant_digitos1 and b==cant_digitos2 and c==cant_digitos3 and d==cant_digitos4:
            MostrarResultados.usuario = self.usuario
            MostrarResultados.edad = self.edad
            MostrarResultados.peso = self.peso
            MostrarResultados.talla = self.talla
            valor1 = float(self.t_score1.text)
            valor2 = float(self.t_score2.text)
            MostrarResultados.valor_dmo1 = float(self.valor_dmo1.text)
            MostrarResultados.valor_dmo2 = float(self.valor_dmo2.text)
            MostrarResultados.t_score1 = valor1
            MostrarResultados.t_score2 = valor2
            MostrarResultados.paciente = self.paciente
            MostrarResultados.sexo = self.sexo
            MostrarResultados.fractura = self.fractura
            MostrarResultados.fuma = self.fuma
            self.reset()
            sm.current = 'mostrar_resultados'
        else:
            datos_incorrectos(self)
    def regresar_pagina(self):
        self.reset()
        sm.current = 'toma_datos1'   
        
    def reset(self):
        self.t_score1.text = ""
        self.t_score2.text = ""
        self.valor_dmo1.text = ""
        self.valor_dmo2.text = ""
        
    def close_dialog(self,obj):
        self.dialog.dismiss()
            
class MostrarResultados(Screen):
    paciente = ""
    usuario = ""
    edad = ""
    peso = ""
    talla = ""
    sexo = ""
    t_score1 = 0
    t_score2 = 0
    valor_dmo1 = 0
    valor_dmo2 = 0
    fractura = ""
    fuma = ""
    resultado_dmo = ObjectProperty(None)
    resultado_adicional = ObjectProperty(None)
    
    def on_enter(self):
        db.guardar_resultados(self.paciente,self.usuario, self.edad, self.peso, self.talla, self.sexo, self.fractura, self.fuma, self.t_score1, self.t_score2, self.valor_dmo1, self.valor_dmo2)
        if self.t_score1< -2.5 or self.t_score2 < -2.5:
            if self.fractura == "si":
                self.resultado_dmo.text = "Interpretacion Osea: osteoporosis severa (osteoporosis con fractura)"
            else:    
                self.resultado_dmo.text = 'Interpretacion Osea: osteoporosis'
        else:
            if self.t_score1< -1 or self.t_score2 < -1:
                self.resultado_dmo.text = 'Interpretacion Osea: osteopenia'
            else:
                self.resultado_dmo.text = 'Interpretacion Osea: huesos sanos'
        indice_masa = float(self.peso)/pow(float(self.talla)/100, 2)
        indice_masa = truncate(indice_masa, 1)
        self.resultado_adicional.text = 'El indice de masa del paciente es ' + str(indice_masa)
        if indice_masa >25 or indice_masa<18.5:
            self.resultado_adicional.text += ", no se encuentra en el rango aceptable"
        else:
            self.resultado_adicional.text += ", se encuentra dentro del rango aceptable"
        
        if int(self.edad)>40:
            self.resultado_adicional.text += ". Ademas, es propenso a contraer osteoporosis o mantenerla, debido a su edad"
        else:
            
            self.resultado_adicional.text += ". Ademas, o esn propenso a contraer osteoporosis o mantenerla, debido a su edad"
    
    def recomendaciones(self):
        RecomendacionesMedico.edad = self.edad
        RecomendacionesMedico.peso = self.peso
        RecomendacionesMedico.talla = self.talla
        RecomendacionesMedico.sexo = self.sexo
        RecomendacionesMedico.t_score1 = self.t_score1
        RecomendacionesMedico.t_score2 = self.t_score2
        RecomendacionesMedico.fractura = self.fractura
        RecomendacionesMedico.fuma = self.fuma
        sm.current = 'recomendaciones_medico'
    
    def eliminar_registro(self):
        
        check_string = '¿Estas seguro de querere eliminar el registro del paciente?'
        eliminar_boton = MDFlatButton(text='Si', on_release=self.eliminar)
        cerrar_boton = MDFlatButton(text='Mantener registro', on_release=self.close_dialog)
        self.dialog = MDDialog(title='Advertencia', text=check_string,
                               size_hint=(0.7,0.6), buttons=[eliminar_boton, cerrar_boton])
        self.dialog.open()
    
    def eliminar(self, obj):
        self.close_dialog(self)
        self.reset()
        db.Borrar_Registro(self.usuario, self.paciente)
        check_string = 'El registro ha sido eliminado exitosamente'
        cerrar_boton = MDFlatButton(text='Ok', on_release=self.close_dialog)
        self.dialog = MDDialog(title='Registro eliminado', text=check_string,
                               size_hint=(0.7,0.6), buttons=[cerrar_boton])
        self.dialog.open()
        sm.current = 'menu_medico'
    
    def reset(self):
        self.resultado_dmo.text = ''
        self.resultado_adicional.text = ''
        
    def close_dialog(self, obj):
        self.dialog.dismiss()
        
class RecomendacionesMedico(Screen):
    edad = ""
    peso = ""
    talla = ""
    sexo = ""
    t_score1 = 0
    t_score2 = 0
    fractura = ""
    fuma = ""
    fumador = ObjectProperty(None)
    imc = ObjectProperty(None)
    res_ost = ObjectProperty(None)
    res_edad = ObjectProperty(None)
    
    def on_enter(self):
        indice_masa = float(self.peso)/pow(float(self.talla)/100, 2)
        if self.fuma == "si":
            self.fumador.text = "1)Se recomienda dejar de fumar"
        else:
            self.fumador.text = "1)Mantener el habito de no fumar"
        if indice_masa>18.5 and indice_masa<25.0:
            self.imc.text = "2)Mantener una alimentacion equilibrada"
        else:
            self.imc.text = "2)Regule su alimentacion para un peso correcto"
        if self.t_score1 < -2.5 or self.t_score2 < -2.5:
            self.res_ost.text = "3)Se recomienda consumir alimentos con calcio y vitamina D, evitar cualquier golpe"
        else:
            if self.t_score1 < -1.0 or self.t_score2 < -1.0:
                self.res_ost.text = "3)Realizarse chequeos constantes y consumir calcio y vitamina D para evitar osteoporosis"
            else:
                self.res_ost.text = "3)Seguir con los chequeos y mantener el insumo de calcio y vitamina D para mantenerse sano"
        if int(self.edad)>40:
            if self.sexo == "femenino":
                self.res_edad.text = "4)Los huesos de debilitan luego de la menopausia, tener especial cuidado"
            else:
                self.res_edad.text = "4)Con la edad, los huesos se debilitan. Tener Cuidado."
        else:
            self.res_edad.text = "4)Mantener un cuidado constante a temprana edad para evitar complicaciones"
                
    def reset(self):
        self.fumador.text = ""
        self.imc.text = ""
        self.res_ost.text = ""
        self.res_edad.text = ""

class RegistroPacientes(Screen):
    usuario = ""
    box = ObjectProperty(None)
    b = 0
    lista = []
    def on_enter(self):
        cant_pacientes = db.get_amount_pacients(self.usuario)
        if cant_pacientes !=-1:
            for i in range(cant_pacientes):
                paciente = db.get_name_pacient(self.usuario, i)
                t_score2 = db.get_t_score2(paciente, "Toma 0")
                t_score1 = db.get_t_score1(paciente, "Toma 0")
                fractura = db.get_fractura(paciente, "Toma 0")
                fecha = db.get_date_toma(paciente, "Toma 0")
                if float(t_score1)<-2.5 or float(t_score2)<-2.5:
                    if fractura == "si":
                        estado_actual = "Sufre Osteoporosis Severa"
                    else:
                        estado_actual = "Sufre Osteoporosis"
                else:
                    if float(t_score1)<-1.0 or float(t_score2)<-1.0:
                        estado_actual = "Sufre Osteopenia"
                    else:
                        estado_actual = "Se encuentra bien"
                p = ThreeLineListItem(text= paciente,
                secondary_text = "Estado Actual: " + estado_actual,
                tertiary_text= "Fecha de registro: " + fecha,
                font_style = 'H6', secondary_font_style = 'Subtitle1', tertiary_font_style = 'Subtitle2'
                )
                self.lista.append(p)
                self.box.add_widget(p)
                self.b+=1
        else:
           check_string = 'Usted no cuenta con pacientes ingresados'
           cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
           self.dialog = MDDialog(title='Sin registro de pacientes', text=check_string,
                            size_hint=(0.7,0.6), buttons=[cerrar_botton])
           self.dialog.open() 
    def close_dialog(self,obj):
        self.dialog.dismiss()
        sm.current = 'menu_medico'
    def reset(self):
        for i in range(self.b):
            self.box.remove_widget(self.lista[i])
        self.lista = []
        self.b = 0
        
class PacienteScreen(Screen):
    dni = ObjectProperty(None)
    def ingresar(self):
        cant_digitos = 0
        for c in self.dni.text:
            cant_digitos += 1
        if self.dni.text.isdigit():
            if cant_digitos == 8:    
                if db.validar_paciente(self.dni.text) == 1:
                    MenuPaciente.dni = self.dni.text
                    sm.current='menu_paciente'
                else:
                    check_string = 'Ingrese un DNI que esté vinculado.'
                    cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                    self.dialog = MDDialog(title='Paciente No Encontrado', text=check_string,
                                           size_hint=(0.7,0.6), buttons=[cerrar_botton])
                    self.dialog.open()
            else:
                IngresoInvalido(self)
        else:
            datos_incorrectos(self)
        self.reset()
    def reset(self):
        self.dni.text = ""
    def close_dialog(self,obj):
        self.dialog.dismiss()

class MenuPaciente(Screen):
    dni = ""
    def ver_resultados(self):
        ResultadosPaciente.dni = self.dni
        sm.current='resultados_paciente'
    def datos_medico(self):
        DatosMedico.dni = self.dni
        sm.current='datos_medico'
    def ver_historial(self):
        HistorialPaciente.dni = self.dni
        sm.current='historial_paciente'
        
class HistorialPaciente(Screen):
    dni = ""
    b = 0
    lista = []
    pacient = ObjectProperty(None)
    num_toma = ObjectProperty(None)
    box = ObjectProperty(None)
    
    def on_enter(self):
        self.pacient.text = "Se muestran todos los registros realizados"
        cant_tomas = db.Obtener_Numero_Tomas(self.dni)
        for i in range(cant_tomas):
            toma = "Toma " + str(i + 1)
            fecha = db.get_date_toma(self.dni, toma)
            objeto_lista = TwoLineListItem(text= toma,
                        secondary_text = 'Fecha: ' + fecha,
                        font_style = 'H6', secondary_font_style = 'Subtitle1')
            self.box.add_widget(objeto_lista)
            self.lista.append(objeto_lista)
            self.b+=1
            
    def buscar_toma(self):
        valido = 0
        for i in range(self.b):
            toma = "Toma " + str(i +1)
            if self.num_toma.text.title() == toma:
                valido = 1
        if valido==1:
            RegistroFinal.toma = self.num_toma.text.title()
            RegistroFinal.dni = self.dni
            self.reset_all()
            sm.current = 'registro_final'
        else:
            check_string = 'Ingrese una toma valida entre las mostradas'
            cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
            self.dialog = MDDialog(title='Error en la busqueda', text=check_string,
                    size_hint=(0.7,0.6), buttons=[cerrar_botton])
            self.dialog.open()
            self.reset()
        
    def reset(self):
        self.num_toma.text = ""
        
    def reset_all(self):
        self.pacient.text = ""
        self.num_toma.text = ""
        for i in range(self.b):
            self.box.remove_widget(self.lista[i])
        self.lista = []
        self.b = 0
    
    def close_dialog(self, obj):
        self.dialog.dismiss()
        
class RegistroFinal(Screen):
    dni = ""
    toma = ""
    fecha_toma = ObjectProperty(None)
    edad_peso_talla = ObjectProperty(None)
    t_score1 = ObjectProperty(None)
    t_score2 = ObjectProperty(None)
    fract = ObjectProperty(None)
    res_ost = ObjectProperty(None)
    label1 = ObjectProperty(None)
    label2 = ObjectProperty(None)
    
    def on_enter(self):
        self.label1.text = 'DMO/T-Score Cuello Femoral:'
        self.label2.text = 'DMO/T-Score Columna Vertebral (L1 L3):'
        fecha = db.get_date_toma(self.dni, self.toma)
        edad = db.get_edad(self.dni, self.toma)
        talla = db.get_talla(self.dni, self.toma)
        peso = db.get_peso(self.dni, self.toma)
        t_score1 = db.get_t_score1(self.dni, self.toma)
        t_score2 = db.get_t_score2(self.dni, self.toma)
        fractura = db.get_fractura(self.dni, self.toma)
        dmo1 = db.get_dmo1(self.dni, self.toma)
        dmo2 = db.get_dmo2(self.dni, self.toma)
        self.fecha_toma.text = "Fecha: " + fecha
        self.edad_peso_talla.text = "Edad " + edad + ", Talla " + talla + "cm, Peso " + peso + "kg"
        self.t_score1.text = str(dmo1) + "g/cm^2    //    " + str(t_score1)
        self.t_score2.text = str(dmo2) + "g/cm^2    //    " + str(t_score2)
        if fractura == "si":
            self.fract.text = "Presenta al menos una fractura"
        else:
            self.fract.text = "No tiene fracturas actuales"
        if float(t_score1)<-2.5 or float(t_score2)<-2.5:
            if fractura == "si":
                self.res_ost.text = "Estado: El paciente tiene osteoporosis severa (con fractura)"
            else:
                self.res_ost.text = "Estado: Es paciente tiene osteoporosis"
        else:
            if float(t_score1)<-1.0 or float(t_score2)<-1.0:
                self.res_ost.text = "Estado: El paciente tiene osteopenia"
            else:
                self.res_ost.text = "Estado: El paciente se encuentra bien"
    
    def reset(self):
        self.fecha_toma.text = ""
        self.edad_peso_talla.text = ""
        self.t_score1.text = ""
        self.t_score2.text = ""
        self.fract.text = ""
        self.res_ost.text = ""
        self.label1.text = ""
        self.label2.text = ""
        
        
class ResultadosPaciente(Screen):
    dni = ""
    resultado_ost = ObjectProperty(None)
    indice_masa_corporal = ObjectProperty(None)
    res_imc = ObjectProperty(None)
    res_edad = ObjectProperty(None)
    
    def on_enter(self):
        t_score1 = db.get_t_score1(self.dni, "Toma 0")
        t_score2 = db.get_t_score2(self.dni, "Toma 0")
        peso = float(db.get_peso(self.dni, "Toma 0"))
        talla = float(db.get_talla(self.dni, "Toma 0"))/100
        fractura = db.get_fractura(self.dni, "Toma 0")
        indice_masa = peso/pow(talla, 2)
        indice_masa = truncate(indice_masa, 1)
        edad = db.get_edad(self.dni, "Toma 0")
        if float(t_score1) <-2.5 or float(t_score2)<-2.5:
            if(fractura == "si"):
                self.resultado_ost.text = "Usted tiene OSTEOPOROSIS SEVERA (fractura actual)"
            else:
                self.resultado_ost.text = "Usted tiene OSTEOPOROSIS"
        else:
            if float(t_score1)<-1.0 or float(t_score2)<-1.0:
                self.resultado_ost.text = "Usted tiene OSTEOPENIA"
            else:
                self.resultado_ost.text = "Usted se encuentra bien"
        self.indice_masa_corporal.text = "Su indice de masa corporal es " + str(indice_masa)
        if indice_masa <18.5:
            self.res_imc.text = "Está por debajo de su peso normal"
        elif indice_masa <25:
            self.res_imc.text = "Está en su peso normal"
        elif indice_masa <30:
            self.res_imc.text = "Está con un sobrepeso"
        else:
            self.res_imc.text = "Sufre de obesidad"
        if int(edad) > 40:
            self.res_edad ="Se encuentra en la edad de riesgo donde se debilitan los huesos"
        else:
            self.res_edad = "No se encuentra en la edad de riesgo donde los huesos se debilitan rapidamente"
    
    def recomendaciones(self):
        RecomendacionesPaciente.dni = self.dni
        sm.current = "recomendaciones_paciente"
           
    def reset(self):
        self.indice_masa_corporal.text = ""
        self.res_imc.text = ""
        self.resultado_ost.text = ""
        
class RecomendacionesPaciente(Screen):
    dni = ""
    fumador = ObjectProperty(None)
    imc = ObjectProperty(None)
    res_ost = ObjectProperty(None)
    res_edad = ObjectProperty(None)
    
    def on_enter(self):
        t_score1 = db.get_t_score1(self.dni, "Toma 0")
        t_score2 = db.get_t_score2(self.dni, "Toma 0")
        peso = float(db.get_peso(self.dni, "Toma 0"))
        talla = float(db.get_talla(self.dni, "Toma 0"))/100
        indice_masa = peso/pow(talla, 2)
        fuma = db.get_fuma(self.dni)
        edad = db.get_edad(self.dni, "Toma 0")
        
        if fuma == "si":
            self.fumador.text = "1) Deberia evitar el consumo de tabaco."
        else:
            self.fumador.text = "1) Mantenga el habito de evitar el tabaco."
        if float(t_score1)<-2.5 or float(t_score2)<-2.5:
            self.res_ost.text = "3) Es necesario consumir calcio y vitamina D (como higado), evitar cualquier golpe."
        else:
            if float(t_score1)<-1.0 or float(t_score2)<-1.0:
                self.res_ost.text = "3) Se recomienda incrementar el consumo de calcio y vitamina D para evitar osteoporosis."
            else:
                self.res_ost.text = "3) Mantenga el consumo de calcio y vitamina D para evitar el deterioro de sus huesos."
        if indice_masa>25 or indice_masa<18.5:
            self.imc.text = "2) Regule mejor su alimentacion para equilibrar su peso."
        else:
            self.imc.text = "2) Una buena alimentacion mejora y regula su estado general."
        if int(edad)>40:
            self.res_edad.text = "4) A mayor edad, hay una probabilidad de padecer osteoporosis. Realice un chequeo medico cada 6 meses."
        else:
            self.res_edad.text = "4) Realizarse chequeos medicos anualmente y seguir con dichos analisis para garantizar una buena salud."
    
    def reset(self):
        self.fumador.text = ""
        self.res_ost.text = ""
        self.imc.text = ""
        self.res_edad.text = ""
        
class DatosMedico(Screen):
    dni = ""
    nombre_medico = ObjectProperty(None)
    correo = ObjectProperty(None)
    celular = ObjectProperty(None)
    texto_adicional = ObjectProperty(None)
    
    def on_enter(self):
        medico = db.get_medico(self.dni)
        correo_medico = db.get_correo_medico(medico)
        celular_medico = db.get_celular_medico(medico)
        self.nombre_medico.text = medico
        self.correo.text = 'Su correo vinculado es ' + str(correo_medico)
        self.celular.text = 'Su número de celular es ' + str(celular_medico)
        self.texto_adicional.text = 'Para alguna consulta adicional, comunicarse con su médico encargado'
    
    def reset(self):
        self.nombre_medico.text = ""
        self.correo.text = ""
        self.celular.text = ""
        self.texto_adicional.text = ""

class CrearUsuario(Screen):
    email = ObjectProperty(None)
    usuario = ObjectProperty(None)
    numero = ObjectProperty(None)
    clave = ObjectProperty(None)
    def validar_crear_usuario(self):
        cant_numeros = 0
        print(self.email.text)
        for c in self.numero.text:
            cant_numeros+=1
        if self.usuario.text != "" and self.clave.text != "" and self.numero.text.isdigit() and cant_numeros== 9:
            if len(self.usuario.text)<=14:
                if db.add_user(self.email.text, self.usuario.text, self.clave.text, self.numero.text)==0:
                    sm.current = "medico"
                    self.reset()
                else:
                    if db.add_user(self.email.text,self.usuario.text, self.clave.text, self.numero.text) ==-2:
                        check_string = 'El numero ingresado ya se encuentra vinculado a una cuenta'
                        cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                        self.dialog = MDDialog(title='Error del numero', text=check_string,
                                              size_hint=(0.7,1), buttons=[cerrar_botton])
                        self.dialog.open()
                        self.numero.text = ""
                    elif db.add_user(self.email.text,self.usuario.text, self.clave.text, self.numero.text) !=-3:
                        check_string = 'Ingrese un email valido y que no este vinculado, con una clave con minimo 6 caracteres.'
                        cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                        self.dialog = MDDialog(title='Error del email', text=check_string,
                                              size_hint=(0.7,1), buttons=[cerrar_botton])
                        self.dialog.open()
                        self.email.text = ""
                    else:
                        check_string = 'Ingrese un usario que sea válido.'
                        cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                        self.dialog = MDDialog(title='El usuario ya existe', text=check_string,
                                              size_hint=(0.7,1), buttons=[cerrar_botton])
                        self.dialog.open()
                        self.usuario.text = ""
            else:
                check_string = 'El usuario debe tener como maximo 14 caracteres'
                cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                self.dialog = MDDialog(title='Error de Usuario', text=check_string,
                                              size_hint=(0.7,1), buttons=[cerrar_botton])
                self.dialog.open()
                self.usuario.text = ""
        else:
            invalidForm(self)
    def reset(self):
        self.email.text = ""
        self.usuario.text = ""
        self.clave.text = ""
        self.numero.text = ""
        
    def close_dialog(self,obj):
        self.dialog.dismiss()
    
class RecuperarCuenta(Screen):
    usuario = ObjectProperty(None)
    numero = ObjectProperty(None)
    correo = ObjectProperty(None)
    def validar_recuperar_usuario(self):
        if self.usuario.text != '' and self.numero.text != '' and self.correo.text !='': 
            if db.validate_existent(self.usuario.text, self.numero.text, self.correo.text):
                db.reset_account(self.correo.text)
                cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                check_string = "Se ha enviado un correo para recuperar su cuenta."
                self.dialog = MDDialog(title='Clave Recuperada', text=check_string,
                              size_hint=(0.7,1), buttons=[cerrar_botton])
                self.dialog.open()
                self.reset()
            
            else:
                IngresoInvalido(self)
        else:
            invalidForm(self)
    def close_dialog(self,obj):
        sm.current = 'medico'
        self.dialog.dismiss()
        
    def reset(self):
        self.usuario.text = ""
        self.numero.text = ""
        self.correo.text = ""
        
class WindowManager(ScreenManager):
    pass

def IngresoInvalido(self):
    check_string = 'Los datos ingresados son incorrectos'
    cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                     
    self.dialog = MDDialog(title='Chequeo de datos', text=check_string,
                          size_hint=(0.85,0.6), buttons=[cerrar_botton])
    self.dialog.open()
    
def invalidForm(self):
    check_string = 'Por favor, ingrese todos los requeridos requeridos'
    cerrar_botton = MDFlatButton(text='Ok', on_release=self.close_dialog)
                     
    self.dialog = MDDialog(title='Datos sin completar', text=check_string,
                          size_hint=(0.85,0.6), buttons=[cerrar_botton])
    self.dialog.open()
    
def ValidarRetorno(self):
    check_string = 'Se perderan todos los datos ingresados'
    cerrar_botton = MDFlatButton(text='Si', on_release = (self.retornar_pantalla))
    quedarse_botton = MDFlatButton(text='Prefiero quedarme', on_release=self.close_dialog)
    
    self.dialog = MDDialog(title='¿Estas seguro de regresar?', text=check_string,
                            size_hint=(0.85,0.6), buttons=[cerrar_botton, quedarse_botton])
    self.dialog.open()

def Validar_Salir_Sesion(self):
    check_string = 'Estas seguro que quieres salir de la sesion actual?'
    cerrar_botton = MDFlatButton(text='Si', on_release = (self.salir))
    quedarse_botton = MDFlatButton(text='Prefiero quedarme', on_release=self.close_dialog)
    
    self.dialog = MDDialog(title='Salir de la Sesion', text=check_string,
                            size_hint=(0.85,0.6), buttons=[cerrar_botton, quedarse_botton])
    self.dialog.open()

def datos_incorrectos(self):
    check_string = 'Se deben ingresar el tipo de dato correcto en cada opcion.'
    cerrar_botton = MDFlatButton(text='Ok', on_release = (self.close_dialog))
    self.dialog = MDDialog(title='Datos Ingresados No son Correctos', text=check_string,
                            size_hint=(0.85,0.6), buttons=[cerrar_botton])
    self.dialog.open()

def error_contrasena(self):
    check_string = 'Las claves no son las mismas. Intentelo nuevamente.'
    cerrar_botton = MDFlatButton(text='Ok', on_release = (self.close_dialog))
    self.dialog = MDDialog(title='Datos Incorrectos', text=check_string,
                            size_hint=(0.85,0.6), buttons=[cerrar_botton])
    self.dialog.open()

def contrasena_repetida(self):
    check_string = 'La nueva clave a asignar debe ser diferente a la clave actual.'
    cerrar_botton = MDFlatButton(text='Ok', on_release = (self.close_dialog))
    self.dialog = MDDialog(title='Datos Incorrectos', text=check_string,
                            size_hint=(0.85,0.6), buttons=[cerrar_botton])
    self.dialog.open()

sm = WindowManager()


class VentanasApp(MDApp):
    def build(self):
        self.root = Builder.load_file("ventanas.kv")
        
        self.theme_cls.primary_palette ='Blue'
        screens = [MenuScreen(name="menu"), MedicoScreen(name="medico"),PacienteScreen(name="paciente"),
           CrearUsuario(name="crear_usuario"), RecuperarCuenta(name="recuperar_cuenta"),MenuMedico(name="menu_medico"),
           TomaDatos1(name="toma_datos1"), TomaDatos2(name="toma_datos2"), MostrarResultados(name="mostrar_resultados"),
           PerfilMedico(name="perfil_medico"), CambiarClave(name='cambiar_clave'), RegistroPacientes(name='registro_pacientes'),
           MenuPaciente(name="menu_paciente"), ResultadosPaciente(name="resultados_paciente"), DatosMedico(name="datos_medico"),
           BusquedaPacientes(name="busqueda_pacientes"), Toma_Paciente(name="toma_paciente"), Toma_Paciente_Final(name="toma_paciente_final"),
           RecomendacionesMedico(name="recomendaciones_medico"), RecomendacionesPaciente(name="recomendaciones_paciente"),
           HistorialPaciente(name="historial_paciente"),RegistroFinal(name="registro_final")]

        for screen in screens:
            sm.add_widget(screen)
        
        sm.current = "menu"
        return sm
    
VentanasApp().run()