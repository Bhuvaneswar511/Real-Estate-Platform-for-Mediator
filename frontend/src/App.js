import React, { useState } from 'react';
import { useTranslation } from 'react-i18next'; 
import AddPropertyForm from './AddPropertyForm';
import PropertyList from './PropertyList';
import './App.css';

function App() {
  const { t, i18n } = useTranslation('common'); 
  const [activeTab, setActiveTab] = useState('view');

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>{t('real_estate_platform')}</h1>
        <div className="language-switcher">
          <button onClick={() => changeLanguage('en')} className={i18n.language === 'en' ? 'active-lang' : ''}>English</button>
          <button onClick={() => changeLanguage('kn')} className={i18n.language === 'kn' ? 'active-lang' : ''}>ಕನ್ನಡ (Kannada)</button>
          <button onClick={() => changeLanguage('te')} className={i18n.language === 'te' ? 'active-lang' : ''}>తెలుగు (Telugu)</button> 
        </div>
        <nav>
          <button
            className={activeTab === 'add' ? 'active' : ''}
            onClick={() => setActiveTab('add')}
          >
            {t('add_new_property')}
          </button>
          <button
            className={activeTab === 'view' ? 'active' : ''}
            onClick={() => setActiveTab('view')}
          >
            {t('view_filter_properties')}
          </button>
        </nav>
      </header>
      <main>
        {activeTab === 'add' ? <AddPropertyForm /> : <PropertyList />}
      </main>
    </div>
  );
}

export default App;