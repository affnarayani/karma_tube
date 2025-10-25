import {GoogleGenAI} from '@google/genai';
import wav from 'wav';
import fs from 'fs/promises'; // Added for file system operations
import dotenv from 'dotenv'; // Added for loading environment variables
import path from 'path'; // Added for path manipulation

dotenv.config(); // Load environment variables from .env file

async function saveWaveFile(
   filename,
   pcmData,
   channels = 1,
   rate = 24000,
   sampleWidth = 2,
) {
   return new Promise((resolve, reject) => {
      const writer = new wav.FileWriter(filename, {
            channels,
            sampleRate: rate,
            bitDepth: sampleWidth * 8,
      });

      writer.on('finish', resolve);
      writer.on('error', reject);

      writer.write(pcmData);
      writer.end();
   });
}

async function main() {
   // Initialize GoogleGenAI with API key from .env
   const ai = new GoogleGenAI(process.env.GEMINI_API_KEY);

   // Read config.json to get selected_god and corresponding voiceName
   const configPath = path.join(process.cwd(), 'config.json');
   const configContent = await fs.readFile(configPath, 'utf8');
   const config = JSON.parse(configContent);

   const selectedGod = config.selected_god;
   const voiceKey = `voice_${selectedGod}`;
   const voiceName = config[voiceKey];
   console.log(`Selected God: ${selectedGod}`);
   console.log(`Voice Name: ${voiceName}`);

   // Read content from temp/advice.txt
   let adviceContent = '';
   try {
      adviceContent = await fs.readFile('temp/advice.txt', 'utf8');
   } catch (error) {
      console.error('Error reading temp/advice.txt:', error);
      console.error('Exiting with error code 1 because temp/advice.txt does not exist.');
      process.exit(1);
   }

   const textToSpeak = `Speak with commanding calm — confident, wise, and divine — as though a God is offering compassionate guidance: ${adviceContent}`;

   const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-tts",
      contents: [{ parts: [{ text: textToSpeak }] }],
      config: {
            responseModalities: ['AUDIO'],
            speechConfig: {
               voiceConfig: {
                  prebuiltVoiceConfig: { voiceName: voiceName },
               },
            },
      },
   });

   const data = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
   const audioBuffer = Buffer.from(data, 'base64');

   const fileName = 'temp/speech.wav'; // Save to temp/speech.wav
   await fs.mkdir('temp', { recursive: true }); // Ensure temp directory exists
   await saveWaveFile(fileName, audioBuffer);
   console.log(`Audio saved to ${fileName}`);
}
await main();
