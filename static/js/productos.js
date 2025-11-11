document.addEventListener("DOMContentLoaded", () => {
  // Elementos
  const abrirModalBtn = document.getElementById("abrirModalProducto");
  const cerrarModalBtn = document.getElementById("cerrarModalProducto");
  const modal = document.getElementById("modalOverlayProducto");
  const form = document.getElementById("formProducto");
  const filterSelect = document.getElementById("filterCategoria");
  const productosBody = document.getElementById("productosBody");

  // Abrir modal
  if (abrirModalBtn && modal) {
    abrirModalBtn.addEventListener("click", () => {
      modal.style.display = "flex";
    });
  }

  // Cerrar modal
  if (cerrarModalBtn && modal) {
    cerrarModalBtn.addEventListener("click", () => {
      modal.style.display = "none";
      form.reset();
    });
  }

  // Enviar formulario para crear producto
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const body = new URLSearchParams(formData);

      try {
        const res = await fetch("/productos/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: body
        });

        if (res.ok) {
          alert("✅ Producto agregado exitosamente");
          modal.style.display = "none";
          form.reset();
          // recargar lista: aplicar filtro actual (o todas)
          triggerFilter();
        } else {
          const data = await res.json();
          alert("⚠️ Error: " + (data.detail || JSON.stringify(data)));
          console.error("Error creación producto:", data);
        }
      } catch (err) {
        console.error("Error conexión:", err);
        alert("❌ Error de conexión con el servidor");
      }
    });
  }

  // Filtrar por categoría
  if (filterSelect) {
    filterSelect.addEventListener("change", () => {
      triggerFilter();
    });
  }

  async function triggerFilter() {
    const categoriaId = filterSelect ? filterSelect.value : "0";
    try {
      const res = await fetch(`/productos/categoria/${categoriaId}`);
      if (!res.ok) {
        const err = await res.json();
        alert("Error al filtrar: " + (err.detail || JSON.stringify(err)));
        return;
      }
      const data = await res.json();
      if (data && data.productos) {
        renderProducts(data.productos);
      } else {
        renderProducts([]);
      }
    } catch (err) {
      console.error("Error al obtener productos:", err);
      alert("❌ Error al obtener productos");
    }
  }

  // Renderiza la tabla de productos (reemplaza tbody)
  function renderProducts(productos) {
    if (!productosBody) return;
    productosBody.innerHTML = ""; // limpiar

    if (!productos || productos.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 6;
      td.style.textAlign = "center";
      td.textContent = "No hay productos para mostrar.";
      tr.appendChild(td);
      productosBody.appendChild(tr);
      return;
    }

    productos.forEach(p => {
      const tr = document.createElement("tr");

      const tdId = document.createElement("td");
      tdId.textContent = p.id_producto;
      tr.appendChild(tdId);

      const tdNombre = document.createElement("td");
      tdNombre.textContent = p.nombre;
      tr.appendChild(tdNombre);

      const tdPrecio = document.createElement("td");
      tdPrecio.textContent = Number(p.precio).toFixed(2);
      tr.appendChild(tdPrecio);

      const tdStock = document.createElement("td");
      tdStock.textContent = p.stock;
      tr.appendChild(tdStock);

      const tdCat = document.createElement("td");
      tdCat.textContent = p.categoria_nombre || "";
      tr.appendChild(tdCat);

      const tdAcciones = document.createElement("td");
      const btnEliminar = document.createElement("button");
      btnEliminar.className = "btn-eliminar btn-eliminar-producto";
      btnEliminar.setAttribute("data-id", p.id_producto);
      btnEliminar.textContent = "Eliminar";
      tdAcciones.appendChild(btnEliminar);
      tr.appendChild(tdAcciones);

      productosBody.appendChild(tr);
    });

    // Asignar listeners a botones eliminar
    document.querySelectorAll(".btn-eliminar-producto").forEach(btn => {
      btn.removeEventListener("click", onEliminarClick); // por seguridad
      btn.addEventListener("click", onEliminarClick);
    });
  }

  async function onEliminarClick(e) {
    const id = e.currentTarget.getAttribute("data-id");
    if (!id) return;
    if (!confirm(`¿Eliminar producto ${id}? Esta acción no se puede deshacer.`)) return;

    try {
      const res = await fetch(`/productos/${encodeURIComponent(id)}`, {
        method: "DELETE"
      });
      if (res.ok) {
        alert("✅ Producto eliminado");
        triggerFilter();
      } else {
        const data = await res.json();
        alert("⚠️ Error eliminando: " + (data.detail || JSON.stringify(data)));
      }
    } catch (err) {
      console.error("Error al eliminar:", err);
      alert("❌ Error de conexión al eliminar");
    }
  }

  // Cargar inicialmente (filtrado por 'Todas')
  triggerFilter();

  // Cerrar modal si se hace clic fuera del contenido
  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      if (form) form.reset();
    }
  });
});
