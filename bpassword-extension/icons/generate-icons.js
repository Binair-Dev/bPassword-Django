// Script to convert SVG to PNG icons
// This requires Node.js and canvas/sharp packages
// Run with: node generate-icons.js

const fs = require('fs');
const { createCanvas } = require('canvas');

// Icon sizes
const sizes = [16, 48, 128];

// Read SVG content
const svgContent = fs.readFileSync('icon.svg', 'utf8');

sizes.forEach(size => {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // Draw background
  ctx.fillStyle = '#4CAF50';
  ctx.fillRect(0, 0, size, size);

  // Draw rounded corners
  ctx.beginPath();
  ctx.roundRect(0, 0, size, size, size * 0.15);
  ctx.fillStyle = '#4CAF50';
  ctx.fill();

  // Draw lock body
  const lockX = size * 0.25;
  const lockY = size * 0.44;
  const lockWidth = size * 0.5;
  const lockHeight = size * 0.44;

  ctx.fillStyle = '#2E7D32';
  ctx.strokeStyle = 'white';
  ctx.lineWidth = size * 0.015;
  ctx.beginPath();
  ctx.roundRect(lockX, lockY, lockWidth, lockHeight, size * 0.06);
  ctx.fill();
  ctx.stroke();

  // Draw lock shackle
  const shackleX = size * 0.34;
  const shackleY = size * 0.28;
  const shackleRadius = size * 0.16;

  ctx.strokeStyle = 'white';
  ctx.lineWidth = size * 0.06;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.arc(shackleX + shackleRadius, shackleY + shackleRadius, shackleRadius, Math.PI, 0);
  ctx.stroke();

  // Draw keyhole
  const keyholeX = size * 0.5;
  const keyholeY = size * 0.59;
  const keyholeRadius = size * 0.0625;

  ctx.fillStyle = 'white';
  ctx.beginPath();
  ctx.arc(keyholeX, keyholeY, keyholeRadius, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillRect(keyholeX - keyholeRadius, keyholeY, keyholeRadius * 2, size * 0.19);

  // Save as PNG
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(`icon${size}.png`, buffer);

  console.log(`Generated icon${size}.png`);
});

console.log('All icons generated successfully!');
