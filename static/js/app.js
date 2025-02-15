// app.js para manejar la imagen, clasificacion e historial
document.addEventListener("DOMContentLoaded", function () {
    const inputImagen = document.getElementById("inputImagen");
    const preview = document.getElementById("preview");
    const btnClasificar = document.getElementById("btnClasificar");
    const errorMensaje = document.getElementById("errorMensaje");
    const resultadoEtiqueta = document.getElementById("resultadoEtiqueta");
    const resultadoTexto = document.getElementById("resultadoTexto");
    const btnHistorial = document.getElementById("btnHistorial");
    const btnBorrarHistorial = document.getElementById("btnBorrarHistorial");

    const formatosPermitidos = ["image/jpeg", "image/png", "image/webp"];
    const imagenError = "static/assets/algo salio mal.png";

    if (inputImagen) {
        inputImagen.addEventListener("change", function (event) {
            const file = event.target.files[0];
    
            resultadoEtiqueta.style.display = "none"; //Ocultar resultadoEtiqueta
            resultadoTexto.style.display = "none"; //Ocultar resultadoTexto
            
            if (file && formatosPermitidos.includes(file.type)) {
                errorMensaje.style.display = "none";
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: contain;">`;
                };
                reader.readAsDataURL(file);
                btnClasificar.disabled = false;
            } else {
                errorMensaje.textContent = "Error: Formato de imagen incompatible.";
                errorMensaje.style.display = "block";
                preview.innerHTML = `<img src="${imagenError}" style="width: 100%; height: 100%; object-fit: contain;">`;
                btnClasificar.disabled = true;
            }
        });
    }    
    if (btnClasificar) {
        btnClasificar.addEventListener("click", function () {
            const file = inputImagen.files[0];
            if (!file) return;
    
            const formData = new FormData();
            formData.append("file", file);
    
            fetch("/clasificar", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.resultado) {
                    errorMensaje.style.display = "none"; // Ocultar mensaje de error
                    resultadoEtiqueta.style.display = "block";
                    resultadoTexto.style.display = "block";
                    resultadoTexto.textContent = data.resultado;
                    btnHistorial.removeAttribute("disabled");
                }
            })
            .catch(error => {
                console.error("Error en la petición:", error);
                errorMensaje.textContent = "Error: No se pudo conectar con el servidor.";
                errorMensaje.style.display = "block";
            });
        });
    }

    if (btnHistorial) {
        btnHistorial.addEventListener("click", function () {
            window.open("/historial", "_self");
        });
    }
    
    if (btnBorrarHistorial) {
        btnBorrarHistorial.addEventListener("click", function () {
            fetch("/borrar_historial", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message); // Mensaje de confirmación
                location.reload(); // Recargar la página para actualizar la tabla
            })
            .catch(error => console.error("Error al borrar el historial:", error));
        });
    }
    
});
