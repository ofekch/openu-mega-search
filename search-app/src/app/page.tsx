import { getIndices } from '../lib/db';
import Content from './content';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const indices = await getIndices();
    return (
      <div className="min-h-screen flex flex-col justify-between bg-gray-50 p-8" dir="rtl">
      {/* Main content */}
      <div className="flex-grow flex flex-col items-center">
        <header className="text-4xl font-bold text-gray-800 mb-6">
      Openu mega search
        </header>
  
        {/* Explanation */}
        <p className="text-lg text-gray-600 mb-8 max-w-md text-center">
        חיפוש לפי תוכן בקבצי המגה של האוניברסיטה הפתוחה.
        מחפש בתיקיות מבחנים וממנים, מחזיר נתיב לתוצאות במגה </p>
        <Content indices={indices} />
      </div>
      <footer className="mt-12 text-center text-sm text-gray-500">
  <p>
    תעזרו לי לשפר את זה: 
    <a href="https://github.com/ofekch/openu-mega-search" className="text-blue-500 hover:underline ml-4 mr-1">GitHub</a>
    דברו איתי: 
    <a href="mailto:ofekch221@gmail.com" className="text-blue-500 hover:underline mr-1">ofekch221@gmail.com</a>
  </p>
</footer>
      </div>
    );
}