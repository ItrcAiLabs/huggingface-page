document.addEventListener("click", function(e) {
    if (e.target.tagName === "TH" && e.target.hasAttribute("data-sortable")) {
        const th = e.target;
        const tableId = th.getAttribute("data-table");
        const table = document.getElementById(tableId);
        const tbody = table.querySelector("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr"));
        const colIndex = Array.from(th.parentNode.children).indexOf(th);
        const isAsc = th.classList.contains("asc");

        const clean = (val) => val.replace(/[^0-9.\-]/g, "");

        rows.sort((a, b) => {
            const A = a.children[colIndex].innerText.trim();
            const B = b.children[colIndex].innerText.trim();
            const numA = parseFloat(clean(A));
            const numB = parseFloat(clean(B));
            if (!isNaN(numA) && !isNaN(numB)) {
                return (isAsc ? -1 : 1) * (numA - numB);
            }
            return (isAsc ? -1 : 1) * A.localeCompare(B, 'en', {numeric:true});
        });

        rows.forEach(r => tbody.appendChild(r));

        // reset arrows
        table.querySelectorAll("th").forEach(t => {
            t.classList.remove("asc", "desc");
            const icon = t.querySelector(".sort-icon");
            if (icon) icon.innerText = "⇅";
        });

        if (isAsc) {
            th.classList.remove("asc");
            th.classList.add("desc");
            th.querySelector(".sort-icon").innerText = "↓";
        } else {
            th.classList.remove("desc");
            th.classList.add("asc");
            th.querySelector(".sort-icon").innerText = "↑";
        }
    }
});
