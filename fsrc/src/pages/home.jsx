import { useEffect, useState } from 'react';
import {
  Page,
  Navbar,
  NavLeft,
  NavTitle,
  NavTitleLarge,
  NavRight,
  BlockTitle,
  List,
  ListItem,
  Link,
  Searchbar,
  Icon,
  Toolbar,
  Tabs,
  Tab,
  Block,
  Card,
  CardContent,
  CardHeader,
  Button,
} from 'framework7-react';
import File from './file.jsx';

export default () => {
  const [files, setFile] = useState([]);
  useEffect(() => {
    const url = 'https://jsonplaceholder.typicode.com/albums';
    const options = {};

    fetch(url, options)
      .then((response) => response.json())
      .then((data) => {
        setFile(data);
      });
  }, []);

  return (
    <Page className="page-home">
      <Navbar large transparent sliding={false} mdCenterTitle>
        <NavLeft>
          <Link panelOpen="left" iconIos="f7:menu" iconMd="material:menu" />
        </NavLeft>
        <NavTitle sliding>BrosFiles</NavTitle>
        <NavRight>
          <Link
            searchbarEnable=".searchbar-components"
            iconIos="f7:search"
            iconMd="material:search"
          />
        </NavRight>
        <NavTitleLarge>BrosFiles</NavTitleLarge>
        <Searchbar
          className="searchbar-components"
          searchContainer=".components-list"
          searchIn="a"
          expandable
        />
      </Navbar>

      <Toolbar bottom tabbar>
        <Link tabLink href="/" routeTabId="home">
          <Icon md="material:home" ios="f7:house_fill" slot="media" />
        </Link>
        <Link tabLink href="/subscriptions/" routeTabId="subscriptions">
          <Icon md="material:attach_money" ios="f7:gear_alt_fill" slot="media" />
        </Link>
        <Link tabLink href="/settings/" routeTabId="settings">
          <Icon md="material:settings" ios="f7:gear_alt_fill" slot="media" />
        </Link>
      </Toolbar>
      <Tabs routable>
        <Tab className="page-content" id="home" />
        <Tab className="page-content" id="settings" activeTab />
        <Tab className="page-content" id="subscriptions" />
      </Tabs>

      <BlockTitle className="searchbar-found">Categories</BlockTitle>
      <Block>
        <p>
          In addition to usual <a href="./files/">Files</a>.
        </p>
      </Block>

      <BlockTitle className="searchbar-found">Files</BlockTitle>
      <div className="demo-expandable-cards">

        <Card expandable>
          <CardContent padding={false}>
            <div
              style={{
                background: 'url(./img/beach.jpg) no-repeat center bottom',
                backgroundSize: 'cover',
                height: '240px',
              }}
            />
            <Link
              cardClose
              color="white"
              className="card-opened-fade-in"
              style={{ position: 'absolute', right: '15px', top: '15px' }}
              iconF7="xmark_circle_fill"
            />
            <CardHeader style={{ height: '60px' }}>Beach, Goa</CardHeader>
            <div className="card-content-padding">
              <p>
                test
              </p>
              <p>
                <Button fill round large cardClose>
                  Close
                </Button>
              </p>
            </div>
          </CardContent>
        </Card>

      </div>
      <div className="demo-expandable-cards">
      {files.map((file) => (
        <File file={ file } key={ file.id } />
      ))}
      </div>

    </Page>
  );
};
