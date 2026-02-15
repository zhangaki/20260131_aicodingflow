import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const inputPath = 'public/assets/aeo-mockup.webp';
const outputPath = 'public/assets/aeo-mockup-mobile.webp';

async function resize() {
    try {
        await sharp(inputPath)
            .resize(600) // Resize to 600px width
            .toFile(outputPath);
        console.log(`Created ${outputPath}`);
    } catch (error) {
        console.error("Error resizing image:", error);
    }
}

resize();
