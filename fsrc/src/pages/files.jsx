import { useEffect, useState } from 'react';
import {
  Block,
  BlockTitle,
  Page,
  Navbar,
} from 'framework7-react';
import File from './file.jsx';

export default ({ f7router, navigation }) => {
  const [file, setFile] = useState(null);

  useEffect(() => {
    const url = 'https://jsonplaceholder.typicode.com/albums/1';
    const options = {};

    fetch(url, options)
      .then((response) => response.json())
      .then((data) => {
        setFile(data);
      });
  }, []);

  return (
    <Page>
      <Navbar title="Cards" backLink="Back" />
       <Block>
        <p>
          Cards are a great way to contain and organize your information, especially when combined
        </p>
        <p>
          ads
        </p>
        </Block>

      <File file={ file } />
    </Page>
  );
}
