/* 3D TILT EFFECT 
  Makes elements look at the mouse cursor.
*/

document.addEventListener("mousemove", (e) => {
    document.querySelectorAll(".tilt-card").forEach((card) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left; // Mouse X relative to card
        const y = e.clientY - rect.top;  // Mouse Y relative to card
        
        // Calculate rotation (center of card is 0)
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const maxRotate = 10; 
        
        const rotateX = ((y - centerY) / centerY) * -maxRotate;
        const rotateY = ((x - centerX) / centerX) * maxRotate;

        // Apply styles if mouse is roughly near/over the card to save performance
        card.style.transform = `
            perspective(1000px) 
            rotateX(${rotateX}deg) 
            rotateY(${rotateY}deg) 
            scale3d(1.02, 1.02, 1.02)
        `;
    });
});

// Reset when mouse leaves window or area (optional smooth reset)
document.addEventListener("mouseleave", () => {
    document.querySelectorAll(".tilt-card").forEach((card) => {
        card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)`;
    });
});