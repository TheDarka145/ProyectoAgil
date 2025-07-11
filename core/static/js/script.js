//API PUBLICA 
const nombre = document.querySelector('#nombre');
const correo = document.querySelector('#correo');
const telefono = document.querySelector('#telefono');
const foto = document.querySelector('#foto');

const generarUsuario = async () => {
    const url = 'https://randomuser.me/api/';
    const respuesta = await fetch(url);
    const { results } = await respuesta.json();
    const datos = results[0];

    foto.src = datos.picture.medium;
    nombre.textContent = datos.name.first;
    correo.textContent = datos.email;
    telefono.textContent = datos.phone;
} 

document.addEventListener('DOMContentLoaded', generarUsuario);





