from conexion_BD import conectar_bd
from datetime import date
import bcrypt
from mysql.connector.errors import IntegrityError
import os
import smtplib
from email.message import EmailMessage
import os
import smtplib
from email.message import EmailMessage

# =====================================================================
# GESTIÓN DE USUARIOS Y AUTENTICACIÓN
# =====================================================================

def registrar_usuario(cedula, nombre, password, rol, correo, pregunta, respuesta):
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión con el servidor."
    try:
        cursor = db.cursor()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        sql = """INSERT INTO usuarios 
                 (cedula, nombre_completo, password_hash, rol, correo, pregunta_seguridad, respuesta_seguridad) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (cedula, nombre, hashed_password, rol, correo, pregunta, respuesta))
        db.commit()
        return True, "Usuario registrado correctamente."
    except Exception as e:
        return False, f"Error al registrar usuario: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def obtener_usuarios_priorizados():
    """Recupera los usuarios ordenados por jerarquía de rangos corporativos."""
    db = conectar_bd()
    if not db: 
        return []
    try:
        cursor = db.cursor()
        sql = """SELECT cedula, nombre_completo, rol, correo 
                 FROM usuarios 
                 ORDER BY CASE rol 
                    WHEN 'Administrador' THEN 1 
                    WHEN 'RRHH' THEN 2 
                    WHEN 'Trabajador' THEN 3 
                    ELSE 4 
                 END"""
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def buscar_usuario_por_cedula(cedula):
    """Busca y devuelve la información completa de un usuario específico."""
    db = conectar_bd()
    if not db: 
        return None
    try:
        cursor = db.cursor()
        sql = """SELECT cedula, nombre_completo, rol, correo, pregunta_seguridad, respuesta_seguridad 
                 FROM usuarios WHERE cedula = %s"""
        cursor.execute(sql, (cedula,))
        return cursor.fetchone()
    except Exception:
        return None
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def actualizar_usuario_completo_admin(cedula, nombre, rol, correo, pregunta, respuesta, nueva_pass=None):
    """Actualiza de forma integral el perfil de un usuario desde el panel de administración."""
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión con el servidor."
    try:
        cursor = db.cursor()
        if nueva_pass:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(nueva_pass.encode('utf-8'), salt).decode('utf-8')
            sql = """UPDATE usuarios 
                     SET nombre_completo=%s, rol=%s, correo=%s, pregunta_seguridad=%s, respuesta_seguridad=%s, password_hash=%s 
                     WHERE cedula=%s"""
            cursor.execute(sql, (nombre, rol, correo, pregunta, respuesta, hashed_password, cedula))
        else:
            sql = """UPDATE usuarios 
                     SET nombre_completo=%s, rol=%s, correo=%s, pregunta_seguridad=%s, respuesta_seguridad=%s 
                     WHERE cedula=%s"""
            cursor.execute(sql, (nombre, rol, correo, pregunta, respuesta, cedula))
        db.commit()
        return True, "Datos de usuario actualizados correctamente."
    except Exception as e:
        return False, f"Error al actualizar: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def verificar_trabajador_registrado(cedula):
    db = conectar_bd()
    if not db: 
        return False, None
    try:
        cursor = db.cursor()
        cursor.execute("SELECT apellidos_nombres FROM trabajadores WHERE cedula = %s", (cedula,))
        resultado = cursor.fetchone()
        if resultado:
            return True, resultado[0] 
        return False, None 
    except Exception:
        return False, None
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()


# =====================================================================
# GESTIÓN DE TRABAJADORES E HISTORIAL
# =====================================================================

def registrar_trabajador_completo(cedula, nombres, f_nacimiento, f_ingreso, cargo_inicial):
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión."
    try:
        cursor = db.cursor()
        sql_trabajador = """INSERT INTO trabajadores 
                            (cedula, apellidos_nombres, fecha_nacimiento, fecha_ingreso, cargo_actual, estado_laboral) 
                            VALUES (%s, %s, %s, %s, %s, 'Activo')"""
        cursor.execute(sql_trabajador, (cedula, nombres, f_nacimiento, f_ingreso, cargo_inicial))
        
        sql_historial = """INSERT INTO historial_cargos (cedula_trabajador, cargo, fecha_inicio) 
                           VALUES (%s, %s, %s)"""
        cursor.execute(sql_historial, (cedula, cargo_inicial, f_ingreso))
        
        db.commit()
        return True, "Ficha de empleado e historial inicializados correctamente."
    except Exception as e:
        db.rollback() 
        return False, f"Error al registrar: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def obtener_trabajadores():
    db = conectar_bd()
    if not db: 
        return []
    try:
        cursor = db.cursor()
        sql = "SELECT cedula, apellidos_nombres, cargo_actual, fecha_ingreso, estado_laboral FROM trabajadores"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def promover_o_cambiar_cargo(cedula, nuevo_cargo):
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión."
    hoy = date.today()
    try:
        cursor = db.cursor()
        sql_cerrar = "UPDATE historial_cargos SET fecha_fin = %s WHERE cedula_trabajador = %s AND fecha_fin IS NULL"
        cursor.execute(sql_cerrar, (hoy, cedula))
        
        sql_nuevo = "INSERT INTO historial_cargos (cedula_trabajador, cargo, fecha_inicio) VALUES (%s, %s, %s)"
        cursor.execute(sql_nuevo, (cedula, nuevo_cargo, hoy))
        
        sql_actualizar_ficha = "UPDATE trabajadores SET cargo_actual = %s WHERE cedula = %s"
        cursor.execute(sql_actualizar_ficha, (nuevo_cargo, cedula))
        
        db.commit()
        return True, "Historial de cargos actualizado exitosamente."
    except Exception as e:
        db.rollback()
        return False, f"Error en la actualización: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def consultar_linea_tiempo_cargos(cedula):
    db = conectar_bd()
    if not db: 
        return []
    try:
        cursor = db.cursor()
        sql = "SELECT cargo, fecha_inicio, fecha_fin FROM historial_cargos WHERE cedula_trabajador = %s ORDER BY fecha_inicio DESC"
        cursor.execute(sql, (cedula,))
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()


# =====================================================================
# GESTIÓN DE TRÁMITES Y SOLICITUDES
# =====================================================================

def registrar_solicitud(cedula, tipo_doc):
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión interna."
    try:
        cursor = db.cursor()
        sql = "INSERT INTO solicitudes (cedula_solicitante, tipo_documento, estado) VALUES (%s, %s, 'Pendiente')"
        cursor.execute(sql, (cedula, tipo_doc))
        db.commit()
        return True, "Solicitud enviada correctamente al departamento de RRHH."
    except IntegrityError as e:
        if "foreign key constraint fails" in str(e).lower() or getattr(e, 'errno', 0) == 1452:
            return False, "La cédula no pertenece a un usuario registrado. Debe crear una cuenta."
        return False, f"Error de integridad: {e}"
    except Exception as e:
        return False, f"Error al procesar solicitud: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def obtener_solicitudes():
    db = conectar_bd()
    if not db: 
        return []
    try:
        cursor = db.cursor()
        sql = """
            SELECT s.id, u.nombre_completo, s.tipo_documento, s.estado, s.fecha_solicitud, t.cargo_actual, u.cedula
            FROM solicitudes s
            JOIN usuarios u ON s.cedula_solicitante = u.cedula
            LEFT JOIN trabajadores t ON u.cedula = t.cedula
            ORDER BY s.fecha_solicitud DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def resolver_ticket_solicitud(id_solicitud, nuevo_estado, ruta_guardado=None):
    db = conectar_bd()
    if not db: 
        return False, "Error de conexión."
    try:
        cursor = db.cursor()
        sql = "UPDATE solicitudes SET estado = %s, ruta_archivo = %s WHERE id = %s"
        cursor.execute(sql, (nuevo_estado, ruta_guardado, id_solicitud))
        db.commit()
        return True, "Solicitud actualizada correctamente."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# =====================================================================
# GESTIÓN DE AUDITORÍAS
# =====================================================================

def registrar_auditoria(cedula_usuario, accion, registro_afectado, detalles):
    db = conectar_bd()
    if not db: 
        return False
    try:
        cursor = db.cursor()
        sql = "INSERT INTO auditoria (cedula_usuario, accion, registro_afectado, detalles, fecha_hora) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(sql, (cedula_usuario, accion, registro_afectado, detalles))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al registrar auditoría: {e}")
        return False
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def obtener_auditorias():
    db = conectar_bd()
    if not db: 
        return []
    try:
        cursor = db.cursor()
        sql = "SELECT cedula_usuario, accion, registro_afectado, detalles, fecha_hora FROM auditoria ORDER BY fecha_hora DESC"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener auditorías: {e}")
        return []
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# =====================================================================
# RECUPERACIÓN DE CONTRASEÑA
# =====================================================================

def verificar_correo_usuario(cedula, correo):
    db = conectar_bd()
    if not db:
        return False
    try:
        cursor = db.cursor()
        sql = "SELECT correo FROM usuarios WHERE cedula = %s"
        cursor.execute(sql, (cedula,))
        resultado = cursor.fetchone()
        if resultado and resultado[0].lower() == correo.lower():
            return True
        return False
    except Exception:
        return False
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def enviar_codigo_correo(destinatario, codigo):
    email_origen = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", 587))
    
    if not email_origen or not password or email_origen == "tucorreo@gmail.com":
        print("Configuración de correo incompleta en .env")
        return False, "Servicio de correo no configurado. Contacte a soporte o edite .env."
        
    try:
        msg = EmailMessage()
        msg.set_content(f"Hola,\n\nHas solicitado recuperar tu contraseña en el Sistema de RRHH.\n\nTu código de verificación de 6 dígitos es: {codigo}\n\nSi no fuiste tú, por favor ignora este mensaje.")
        msg['Subject'] = 'Código de Verificación - Recuperación de Contraseña'
        msg['From'] = email_origen
        msg['To'] = destinatario
        
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(email_origen, password)
        server.send_message(msg)
        server.quit()
        return True, "Código enviado exitosamente al correo."
    except Exception as e:
        print(f"Error SMTP: {e}")
        return False, "Error al enviar el correo. Verifique la conexión o credenciales."

def restablecer_password(cedula, nueva_pass):
    db = conectar_bd()
    if not db:
        return False, "Error de conexión con la base de datos."
    try:
        cursor = db.cursor()
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(nueva_pass.encode('utf-8'), salt).decode('utf-8')
        sql = "UPDATE usuarios SET password_hash = %s WHERE cedula = %s"
        cursor.execute(sql, (hashed_pw, cedula))
        db.commit()
        return True, "Contraseña restablecida correctamente."
    except Exception as e:
        return False, f"Error interno: {e}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()