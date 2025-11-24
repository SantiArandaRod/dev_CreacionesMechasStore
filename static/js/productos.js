document.addEventListener("DOMContentLoaded", () => {

  // ===== VARIABLES GLOBALES =====
  let currentPage = 1;
  const PAGE_SIZE = 10;

  // ===== ELEMENTOS =====
  const abrirModalBtn = document.getElementById("abrirModalProducto");
  const cerrarModalBtn = document.getElementById("cerrarModalProducto");
  const modal = document.getElementById("modalOverlayProducto");
  const form = document.getElementById("formProducto");
  const filterSelect = document.getElementById("filterCategoria");
  const productosBody = document.getElementById("productosBody");
  const buscador = document.getElementById("buscador");

  // ============================
  //          MODAL
  // ============================
  if (abrirModalBtn) {
    abrirModalBtn.addEventListener("click", () => {
      modal.style.display = "flex";
    });
  }

  if (cerrarModalBtn) {
    cerrarModalBtn.addEventListener("click", () => {
      modal.style.display = "none";
      form.reset();
    });
  }

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      form.reset();
    }
  });

  // ============================
  //     CREAR PRODUCTO
  // ============================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      const body = new URLSearchParams(formData);

      try {
        const res = await fetch("/productos/", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body
        });

        if (res.ok) {
          alert("Producto agregado exitosamente");
          modal.style.display = "none";
          form.reset();
          obtenerPagina(1);
        } else {
          const err = await res.json();
          alert("Error: " + err.detail);
        }
      } catch (error) {
        alert("Error de conexión");
      }
    });
  }

  // ============================
  //    FILTRO POR CATEGORÍA
  // ============================
  if (filterSelect) {
    filterSelect.addEventListener("change", () => {
      obtenerPagina(1);
    });
  }

  // ============================
  //       BUSCADOR
  // ============================
  if (buscador) {
    buscador.addEventListener("input", () => {
      obtenerPagina(1);
    });
  }

  // ============================
  //     PAGINACIÓN BACKEND
  // ============================
  async function obtenerPagina(page) {
    currentPage = page;

    const categoriaId = filterSelect ? filterSelect.value : 0;
    const search = buscador ? buscador.value.trim() : "";

    try {
      const res = await fetch(
        `/productos/paginados/?page=${page}&page_size=${PAGE_SIZE}&categoria=${categoriaId}&search=${encodeURIComponent(search)}`
      );

      const data = await res.json();

      renderProducts(data.productos);
      renderPaginacion(data.total_pages, data.current_page);

    } catch (err) {
      console.log("Error cargando productos:", err);
      alert("Error cargando productos");
    }
  }

  // ============================
  //         RENDER TABLA
  // ============================
  function renderProducts(productos) {
    productosBody.innerHTML = "";

    if (!productos || productos.length === 0) {
      productosBody.innerHTML = `
        <tr><td colspan="6" style="text-align:center;">No hay productos</td></tr>
      `;
      return;
    }

    productos.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id_producto}</td>
        <td>${p.nombre}</td>
        <td>${Number(p.precio).toFixed(2)}</td>
        <td>${p.stock}</td>
        <td>${p.categoria_nombre}</td>
        <td>
          <button class="btn-eliminar btn-eliminar-producto" data-id="${p.id_producto}">
            Eliminar
          </button>
        </td>
      `;
      productosBody.appendChild(tr);
    });

    document.querySelectorAll(".btn-eliminar-producto").forEach(btn => {
      btn.addEventListener("click", eliminarProducto);
    });
  }

  // ============================
  //     ELIMINAR PRODUCTO
  // ============================
  async function eliminarProducto(e) {
    const id = e.target.getAttribute("data-id");
    if (!confirm(`Eliminar producto ${id}?`)) return;

    try {
      const res = await fetch(`/productos/${encodeURIComponent(id)}`, {
        method: "DELETE"
      });

      if (res.ok) {
        alert("Producto eliminado");
        obtenerPagina(currentPage);
      } else {
        alert("No se pudo eliminar");
      }
    } catch (err) {
      alert("Error de conexión");
    }
  }

  // ============================
  //    RENDER PAGINACIÓN
  // ============================
  function renderPaginacion(totalPages, currentPage) {
    const cont = document.getElementById("paginacion");
    if (!cont) return;

    cont.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.textContent = i;
      btn.className = "volver-button";
      btn.style.padding = "8px 14px";

      if (i === currentPage) {
        btn.style.background = "#6b2d84";
        btn.style.color = "white";
      }

      btn.addEventListener("click", () => obtenerPagina(i));
      cont.appendChild(btn);
    }
  }
// ============================
//   ALERTA STOCK BAJO
// ============================
function mostrarAlertasStock() {
  const alertas = window.alertasStock;

  if (!alertas || alertas.length === 0) return;

  let mensaje = "";

  alertas.forEach(p => {
    mensaje += `⚠️ El producto "${p.nombre}" tiene solo ${p.stock} unidades en stock.\n`;
  });

  alert(mensaje);
}

setTimeout(() => {
  mostrarAlertasStock();
}, 300);


  // ============================
  //    CARGAR PRIMERA PAGINA
  // ============================
  obtenerPagina(1);
});
