import React from 'react';
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

export default () => (
    <Page className="page-settings">
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

      <BlockTitle className="searchbar-found">Private</BlockTitle>
      <Block>
        <p>
          In addition to usual <a href="./files/">Files</a>.
        </p>
      </Block>
    </Page>
);
