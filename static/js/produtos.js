// ============================
// MODAL DE PRODUTOS
// ============================

const modalProduto = document.getElementById("modalProduto");
const formProduto = document.getElementById("product-form");
const btnCadastrar = document.getElementById("btnCadastrar");
const btnFechar = document.querySelector(".fechar");

// ============================
// ABRIR MODAL PARA CADASTRAR
// ============================

btnCadastrar.addEventListener("click", () => {

    formProduto.reset();

    formProduto.action = "/produtos/cadastrar/";

    modalProduto.classList.add("show");

});

// ============================
// FECHAR MODAL
// ============================

btnFechar.addEventListener("click", () => {

    modalProduto.classList.remove("show");

});

// Fecha clicando fora da janela

window.addEventListener("click", function (e) {

    if (e.target === modalProduto) {
        modalProduto.classList.remove("show");
    }

});


// ============================
// EDITAR PRODUTO
// ============================

async function editarProduto(id) {

    try {

        const resposta = await fetch(`/produtos/json/${id}/`);

        if (!resposta.ok) {
            throw new Error("Erro ao buscar produto.");
        }

        const produto = await resposta.json();

        formProduto.action = `/produtos/editar/${id}/`;

        formProduto.nome.value = produto.nome;
        formProduto.categoria.value = produto.categoria;
        formProduto.descricao.value = produto.descricao;
        formProduto.codigo.value = produto.codigo;
        formProduto.marca.value = produto.marca;
        formProduto.preco_venda.value = produto.preco_venda;
        formProduto.preco_custo.value = produto.preco_custo || "";
        formProduto.quantidade.value = produto.quantidade;
        formProduto.validade.value = produto.validade || "";
        formProduto.fornecedor.value = produto.fornecedor || "";

        formProduto.status.checked = produto.status;
        formProduto.destaque.checked = produto.destaque;

        modalProduto.classList.add("show");

    } catch (erro) {

        console.error(erro);
        alert("Erro ao carregar o produto.");

    }

}

console.log("JS Produtos carregado.");