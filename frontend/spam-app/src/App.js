import './App.css';
import EmailComposer from './EmailComposer/ComposerContainer/EmailComposer'
function App() {
  return (
    <div>
      <div class="header">
        <h1>Spam Detection App</h1>
        <p>Write an email in the email composer below and click send. See if the email is classified as spam or ham!</p>
      </div>
      <div class="compose-container">
        <EmailComposer></EmailComposer>
      </div>
    </div>
  );
}

export default App;
