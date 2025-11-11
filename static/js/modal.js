document.addEventListener("DOMContentLoaded", () => {
  const abrir = document.getElementById("abrirModal");
  const cerrar = document.getElementById("cerrarModal");
  const modal = document.getElementById("modalOverlay");
  const form = document.getElementById("formProveedor");

  if (abrir && cerrar && modal && form) {

    // Abrir modal
    abrir.addEventListener("click", () => {
      modal.style.display = "flex";
    });

    // Cerrar modal
    cerrar.addEventListener("click", () => {
      modal.style.display = "none";
    });

    // Enviar datos del proveedor
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch("/proveedores/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams(data),
        });

        if (response.ok) {
          alert("✅ Proveedor agregado exitosamente");
          window.location.reload();
        } else {
          const errorData = await response.json();
          alert("⚠️ Error: " + (errorData.detail || "No se pudo agregar el proveedor"));
        }
      } catch (error) {
        console.error("Error al enviar proveedor:", error);
        alert("❌ Error de conexión con el servidor");
      }
    });
  }
});
