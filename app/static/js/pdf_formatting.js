console.log("Script loaded");

function toggleFullscreen(elementId) {
    const pdfContainer = document.querySelector('.pdf-container');
    const chatContainer = document.querySelector('.chat-container');
    if (elementId === 'pdf') {
        pdfContainer.classList.toggle('fullscreen');
        chatContainer.style.display = pdfContainer.classList.contains('fullscreen') ? 'none' : 'block';
    } else if (elementId === 'chat') {
        chatContainer.classList.toggle('fullscreen');
        pdfContainer.style.display = chatContainer.classList.contains('fullscreen') ? 'none' : 'block';
    }
    console.log('toggleFullscreen');
}

function init_pdf_viewer() {
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const pdfUrl = pdfViewerContainer.getAttribute('data-pdf-url');
    const eventBus = new pdfjsViewer.EventBus();
    // Load the PDF document
    const doc = pdfjsLib.getDocument(pdfUrl);
    doc.promise.then(function(pdfDoc_) {
        // Initialize the viewer with the EventBus
        const viewerContainer = pdfViewerContainer;
        console.log('pdfDoc_');
        console.log(viewerContainer);
        const viewer = new pdfjsViewer.PDFViewer({
            container: viewerContainer,
            eventBus: eventBus,
            pdfDocument: pdfDoc_,
        });

        // Set the viewer document
        viewer.setDocument(pdfDoc_);
        // Track the current page and handle scrolling
        eventBus.on('pagechanging', function (evt) {
            const currentPage = evt.pageNumber;
            console.log('Current Page: ' + currentPage); // Replace with your tracking logic
        });
    });
}
