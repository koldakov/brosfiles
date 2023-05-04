import {
  BlockTitle,
  Button,
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  Link,
  Actions,
  ActionsGroup,
  ActionsButton,
  Progressbar,
} from 'framework7-react';

export default ({ file }) => {
  if (file === null) {
    return (
      <Card outlineMd className="demo-card-header-pic">
        <CardHeader valign="bottom">
          <Progressbar infinite />
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card expandable>
      <CardContent padding={false}>
        <CardHeader style={{ height: '60px' }}>{ file.id }</CardHeader>
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
        <div className="card-content-padding">
          <p>
            { file.title }
          </p>
          <p>
            <Button fill round large cardClose>
              Close
            </Button>
          </p>
        </div>
        <CardFooter>
          <Link>Download</Link>
              <Link fill actionsOpen="#file-actions">Options</Link>
        </CardFooter>
        <Actions id="file-actions">
          <ActionsGroup>
            <ActionsButton color="red">Delete</ActionsButton>
          </ActionsGroup>
        </Actions>
      </CardContent>
    </Card>
//     <Card outlineMd className="demo-card-header-pic">
//       <BlockTitle>{ file.id }</BlockTitle>
//       <CardHeader
//         valign="bottom"
//         style={{
//           backgroundImage: 'url(https://cdn.framework7.io/placeholder/nature-1000x600-3.jpg)',
//         }}
//       >
//       </CardHeader>
//       <CardContent>
//         <p className="date">Posted on January 21, 2015</p>
//         <p>
//           { file.title }
//         </p>
//       </CardContent>
//       <CardFooter>
//         <Link>Download</Link>
//         <Link fill actionsOpen="#file-actions">Like</Link>
//       </CardFooter>
//     <Actions id="file-actions">
//       <ActionsGroup>
//         <ActionsButton color="red">Delete</ActionsButton>
//       </ActionsGroup>
//     </Actions>
//     </Card>
  );
}
