const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');
const toggleSidebarButton = document.getElementById('toggleSidebar');

toggleSidebarButton.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    content.classList.toggle('collapsed');            
});


