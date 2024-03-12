console.log("Script loaded");

// Function to toggle fullscreen mode for either PDF viewer or chat interface
function toggleFullscreen(type) {
    if (type === 'pdf') {
        isPdfFullscreen = !isPdfFullscreen;
        document.getElementById('viewerContainer').classList.toggle('fullScreen', isPdfFullscreen);
    } else if (type === 'chat') {
        isChatFullscreen = !isChatFullscreen;
        document.getElementById('chatContainer').classList.toggle('fullScreen', isChatFullscreen);
    }
}

// Function to toggle between PDF viewer and chat interface
function toggleView(view) {
    if (view === 'pdf') {
        document.getElementById('viewerContainer').style.display = 'block';
        document.getElementById('chatContainer').style.display = 'none';
    } else if (view === 'chat') {
        document.getElementById('viewerContainer').style.display = 'none';
        document.getElementById('chatContainer').style.display = 'block';
    }
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

